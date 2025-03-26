import os

REQUEST_PAYLOAD_FIELDS = os.environ.get("REQUEST_PAYLOAD_FIELDS", "paytmUserId,paytmMerchantId,eventAmount")
REQUEST_METADATA_FIELDS = os.environ.get("REQUEST_METADATA_FIELDS", "customerId")
BASE_FIELDS = os.environ.get("BASE_FIELDS", "actionRecommended,@timestamp,actionRecommendedRuleStatus,source")