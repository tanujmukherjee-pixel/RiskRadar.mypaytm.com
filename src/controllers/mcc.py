"""MCC dashboard API controller."""

import csv
import io

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from ..domains.mcc import MCCBatchResponse, MCCClassifyRequest
from ..services.mcc import MCCService

router = APIRouter(prefix="/mcc", tags=["mcc"])
_service = MCCService()


@router.get("/", include_in_schema=False)
async def dashboard():
    """Serve the MCC dashboard HTML."""
    return FileResponse("static/mcc.html")


@router.post("/classify", response_model=MCCBatchResponse)
async def classify_single(request: MCCClassifyRequest):
    """Classify a single merchant URL."""
    try:
        results = await _service.classify([request.url])
        return MCCBatchResponse(results=results)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/classify/batch", response_model=MCCBatchResponse)
async def classify_batch(file: UploadFile = File(...)):
    """Classify merchant URLs from a CSV file (first column or column named 'url')."""
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        fieldnames = reader.fieldnames or []
        url_col = next(
            (f for f in fieldnames if f.strip().lower() == "url"),
            fieldnames[0] if fieldnames else None,
        )
        if url_col:
            urls = [
                row[url_col].strip() for row in reader if row.get(url_col, "").strip()
            ]
        else:
            # No header — treat each line as a URL
            urls = [line.strip() for line in text.splitlines() if line.strip()]

        if not urls:
            raise HTTPException(status_code=400, detail="No URLs found in CSV")

        results = await _service.classify(urls)
        return MCCBatchResponse(results=results)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/export")
async def export_csv(response: MCCBatchResponse):
    """Export classification results as a CSV file."""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "url",
            "merchant_name",
            "category",
            "mcc_code",
            "confidence",
            "description",
            "error",
        ],
    )
    writer.writeheader()
    for r in response.results:
        writer.writerow(r.model_dump())
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mcc_results.csv"},
    )
