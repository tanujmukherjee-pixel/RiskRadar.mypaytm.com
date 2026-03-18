"""NPCI MCC (Merchant Category Code) reference data — ISO 18245."""

MCC_CODES: dict = {
    # Agriculture
    "0742": {
        "category": "Veterinary Services",
        "description": "Veterinary services for animals",
    },
    "0763": {
        "category": "Agricultural Supplies",
        "description": "Agricultural cooperatives and supplies",
    },
    "0780": {
        "category": "Landscaping / Horticulture",
        "description": "Landscaping and horticultural services",
    },
    # Airlines / Travel
    "3000": {
        "category": "Airlines",
        "description": "United Airlines and other major carriers",
    },
    "4511": {
        "category": "Airlines / Air Carriers",
        "description": "Airlines and air carriers",
    },
    "4722": {
        "category": "Travel Agencies / Tour Operators",
        "description": "Travel agencies and tour operators",
    },
    "4723": {
        "category": "Tour Operators (Germany)",
        "description": "Package tour operators",
    },
    "4784": {"category": "Tolls / Bridge Fees", "description": "Tolls and bridge fees"},
    "4789": {
        "category": "Transportation Services",
        "description": "Other transportation services",
    },
    # Automotive
    "5511": {"category": "Car Dealers (New)", "description": "New automobile dealers"},
    "5521": {
        "category": "Car Dealers (Used)",
        "description": "Used automobile dealers",
    },
    "5531": {
        "category": "Auto Parts / Supplies",
        "description": "Auto parts and accessories stores",
    },
    "5541": {
        "category": "Service Stations / Fuel",
        "description": "Service stations and fuel retailers",
    },
    "5571": {
        "category": "Motorcycle Dealers",
        "description": "Motorcycle shops and dealers",
    },
    "5599": {
        "category": "Automotive Dealers (Misc)",
        "description": "Miscellaneous automotive dealers",
    },
    "7511": {
        "category": "Truck / Utility Trailer Rentals",
        "description": "Truck and utility trailer rentals",
    },
    "7512": {
        "category": "Car Rental Agencies",
        "description": "Automobile rental agencies",
    },
    "7513": {"category": "Truck / Auto Rental", "description": "Truck and auto rental"},
    "7523": {
        "category": "Parking Lots / Garages",
        "description": "Parking lots and garages",
    },
    "7531": {
        "category": "Auto Body Repair",
        "description": "Automotive body repair shops",
    },
    "7534": {
        "category": "Tyre Retreading / Repair",
        "description": "Tyre retreading and repair",
    },
    "7535": {"category": "Auto Paint Shops", "description": "Automotive paint shops"},
    "7538": {
        "category": "Auto Service Shops",
        "description": "Automotive service shops",
    },
    "7549": {"category": "Towing Services", "description": "Towing and road services"},
    # Education
    "8211": {
        "category": "Schools / Educational Services",
        "description": "Elementary and secondary schools",
    },
    "8220": {
        "category": "Colleges / Universities",
        "description": "Colleges, universities and professional schools",
    },
    "8241": {
        "category": "Correspondence Schools",
        "description": "Correspondence schools",
    },
    "8244": {
        "category": "Business / Secretarial Schools",
        "description": "Business and secretarial schools",
    },
    "8249": {
        "category": "Trade / Vocational Schools",
        "description": "Vocational and trade schools",
    },
    "8299": {
        "category": "Educational Services (Misc)",
        "description": "Miscellaneous educational services and schools",
    },
    # Electronics / Technology
    "5045": {
        "category": "Computers / Peripherals (Wholesale)",
        "description": "Computers and peripherals wholesale",
    },
    "5065": {
        "category": "Electrical Parts / Equipment",
        "description": "Electrical parts and equipment",
    },
    "5732": {
        "category": "Electronics Stores",
        "description": "Electronics and appliance stores",
    },
    "5734": {
        "category": "Computer / Software Stores",
        "description": "Computer and software retail stores",
    },
    "5945": {
        "category": "Hobby / Toy / Game Shops",
        "description": "Hobby, toy and game shops",
    },
    "7372": {
        "category": "Computer Programming / Data Processing",
        "description": "Software development and data processing",
    },
    "7371": {
        "category": "IT / Software Services",
        "description": "Computer programming, data processing, IT services",
    },
    "7374": {
        "category": "Data Processing / Tabulating",
        "description": "Data processing and tabulating services",
    },
    "7379": {
        "category": "Computer Maintenance / Repair",
        "description": "Computer maintenance and repair services",
    },
    # Entertainment / Media
    "5815": {
        "category": "Digital Goods / Media",
        "description": "Digital goods — books, movies, music, apps",
    },
    "5816": {"category": "Digital Games", "description": "Digital goods — games"},
    "5817": {
        "category": "Digital Applications",
        "description": "Digital goods — large digital goods merchant",
    },
    "7832": {
        "category": "Motion Picture Theatres",
        "description": "Cinema and motion picture theatres",
    },
    "7841": {
        "category": "DVD / Video Rentals",
        "description": "Video tape and disc rentals",
    },
    "7922": {
        "category": "Theatrical Producers / Ticket Agencies",
        "description": "Theatrical event ticketing",
    },
    "7929": {
        "category": "Entertainment (Misc)",
        "description": "Entertainment bands, orchestras and performers",
    },
    "7941": {
        "category": "Sports Clubs / Teams",
        "description": "Sports clubs, professional teams and promoters",
    },
    "7991": {
        "category": "Tourist Attractions",
        "description": "Tourist attractions and exhibits",
    },
    "7993": {
        "category": "Video Amusement Game Supplies",
        "description": "Video game and amusement arcade supplies",
    },
    "7994": {
        "category": "Video Game Arcades",
        "description": "Video game arcades and establishments",
    },
    "7995": {
        "category": "Betting / Lottery / Casino",
        "description": "Betting, casino gaming chips and lottery tickets",
    },
    # Fashion / Apparel
    "5611": {
        "category": "Men's Clothing Stores",
        "description": "Men's and boys' clothing and furnishings",
    },
    "5621": {
        "category": "Women's Clothing Stores",
        "description": "Women's ready-to-wear stores",
    },
    "5631": {
        "category": "Women's Accessory Stores",
        "description": "Women's accessory and specialty stores",
    },
    "5641": {
        "category": "Children's Clothing Stores",
        "description": "Children's and infants' wear stores",
    },
    "5651": {
        "category": "Family Clothing Stores",
        "description": "Family clothing stores",
    },
    "5661": {"category": "Shoe Stores", "description": "Shoe stores"},
    "5681": {
        "category": "Furriers / Fur Shops",
        "description": "Furriers and fur shops",
    },
    "5691": {
        "category": "Men's / Women's Clothing Stores",
        "description": "Men's and women's clothing stores",
    },
    "5699": {
        "category": "Misc Apparel Stores",
        "description": "Miscellaneous apparel and accessory shops",
    },
    "5940": {
        "category": "Sporting Goods Stores",
        "description": "Sporting goods stores",
    },
    # Financial Services
    "6010": {
        "category": "Banks / Financial Institutions",
        "description": "Manual cash disbursements — banks",
    },
    "6011": {
        "category": "ATM / Cash Dispensing",
        "description": "Automated cash disbursements",
    },
    "6012": {
        "category": "Merchandise and Services — Banks",
        "description": "Financial institutions merchandise",
    },
    "6051": {
        "category": "Non-Financial Institutions — Foreign Exchange",
        "description": "Currency exchange and cheque cashing",
    },
    "6211": {
        "category": "Security Brokers / Dealers",
        "description": "Security brokers, dealers and flotation companies",
    },
    "6300": {
        "category": "Insurance",
        "description": "Insurance sales, underwriting and premiums",
    },
    "6381": {
        "category": "Insurance (Premiums)",
        "description": "Insurance premiums and payments",
    },
    "6399": {
        "category": "Financial Services (Misc)",
        "description": "Financial services not elsewhere classified",
    },
    "6513": {
        "category": "Real Estate Agents / Managers",
        "description": "Real estate agents and managers",
    },
    # Food / Restaurants
    "5411": {
        "category": "Grocery Stores / Supermarkets",
        "description": "Grocery stores and supermarkets",
    },
    "5422": {
        "category": "Meat / Seafood Stores",
        "description": "Freezer and locker meat provisioners",
    },
    "5441": {
        "category": "Candy / Confectionery Stores",
        "description": "Candy, nut and confectionery stores",
    },
    "5451": {
        "category": "Dairy Products Stores",
        "description": "Dairy products stores",
    },
    "5461": {"category": "Bakeries", "description": "Bakeries"},
    "5462": {"category": "Bakeries", "description": "Bakeries — retail"},
    "5499": {
        "category": "Misc Food Stores",
        "description": "Miscellaneous food stores",
    },
    "5812": {
        "category": "Restaurants / Eating Places",
        "description": "Eating places and restaurants",
    },
    "5813": {
        "category": "Bars / Taverns / Lounges",
        "description": "Drinking places — bars, taverns and nightclubs",
    },
    "5814": {
        "category": "Fast Food Restaurants",
        "description": "Fast food restaurants",
    },
    # Government
    "9211": {
        "category": "Court Costs / Fines",
        "description": "Court costs including alimony and child support",
    },
    "9222": {"category": "Fines / Government", "description": "Fines"},
    "9311": {"category": "Tax Payments", "description": "Tax payments"},
    "9399": {
        "category": "Government Services (Misc)",
        "description": "Government services not elsewhere classified",
    },
    "9402": {
        "category": "Postal Services",
        "description": "Postal services — government",
    },
    # Health / Medical
    "5047": {
        "category": "Medical / Dental / Ophthalmic Equipment",
        "description": "Medical and dental equipment supplies",
    },
    "5122": {
        "category": "Drug Stores / Pharmacies",
        "description": "Drugs, drug proprietaries and druggists' sundries",
    },
    "5912": {
        "category": "Drug Stores / Pharmacies (Retail)",
        "description": "Drug stores and pharmacies",
    },
    "8011": {
        "category": "Doctors / Physicians",
        "description": "Doctors and physicians — not elsewhere classified",
    },
    "8021": {
        "category": "Dentists / Orthodontists",
        "description": "Dentists and orthodontists",
    },
    "8031": {
        "category": "Osteopathic Physicians",
        "description": "Osteopathic physicians",
    },
    "8041": {"category": "Chiropractors", "description": "Chiropractors"},
    "8042": {
        "category": "Optometrists / Ophthalmologists",
        "description": "Optometrists and ophthalmologists",
    },
    "8049": {
        "category": "Podiatrists / Chiropodists",
        "description": "Podiatrists and chiropodists",
    },
    "8050": {
        "category": "Nursing / Personal Care Facilities",
        "description": "Nursing and personal care facilities",
    },
    "8062": {"category": "Hospitals", "description": "Hospitals"},
    "8071": {
        "category": "Dental / Medical Laboratories",
        "description": "Medical and dental laboratories",
    },
    "8099": {
        "category": "Health Practitioners (Misc)",
        "description": "Health practitioners not elsewhere classified",
    },
    # Home / Hardware
    "5200": {
        "category": "Home Supply / Hardware Stores",
        "description": "Home supply and hardware stores",
    },
    "5211": {
        "category": "Lumber / Building Materials",
        "description": "Lumber and building material dealers",
    },
    "5251": {"category": "Hardware Stores", "description": "Hardware stores"},
    "5261": {
        "category": "Nurseries / Lawn / Garden Stores",
        "description": "Lawn and garden supply stores",
    },
    "5712": {
        "category": "Furniture / Home Furnishings",
        "description": "Furniture and home furnishing stores",
    },
    "5713": {
        "category": "Floor Covering Stores",
        "description": "Floor covering stores",
    },
    "5714": {
        "category": "Drapery / Upholstery Stores",
        "description": "Drapery, window covering and upholstery stores",
    },
    "5719": {
        "category": "Misc Home Furnishing Stores",
        "description": "Miscellaneous home furnishing specialty stores",
    },
    "5722": {
        "category": "Household Appliance Stores",
        "description": "Household appliance stores",
    },
    # Hotels / Accommodation
    "7011": {
        "category": "Hotels / Motels / Resorts",
        "description": "Lodging — hotels, motels and resorts",
    },
    "7012": {"category": "Timeshares", "description": "Timeshares"},
    "7021": {
        "category": "Rooming / Boarding Houses",
        "description": "Rooming and boarding houses",
    },
    "7032": {
        "category": "Sporting / Recreational Camps",
        "description": "Sporting and recreational camps",
    },
    "7033": {
        "category": "Trailer Parks / Campgrounds",
        "description": "Trailer parks and campgrounds",
    },
    "7041": {
        "category": "Membership Hotels / Lodging",
        "description": "Membership hotels and lodging",
    },
    # Online / E-Commerce
    "5964": {
        "category": "Direct Marketing — Catalogue",
        "description": "Direct marketing catalogue merchants",
    },
    "5965": {
        "category": "Direct Marketing — Combined Catalogue",
        "description": "Direct marketing catalogue and retail merchants",
    },
    "5966": {
        "category": "Direct Marketing — Outbound Telemarketing",
        "description": "Direct marketing outbound telemarketing",
    },
    "5967": {
        "category": "Direct Marketing — Inbound Telemarketing",
        "description": "Direct marketing inbound telemarketing",
    },
    "5968": {
        "category": "Direct Marketing — Subscription",
        "description": "Direct marketing continuity and subscription",
    },
    "5969": {
        "category": "Direct Marketing (Misc)",
        "description": "Miscellaneous direct marketing merchants",
    },
    # Professional Services
    "7389": {
        "category": "Business Services (Misc)",
        "description": "Services not elsewhere classified — business",
    },
    "7392": {
        "category": "Management / Consulting Services",
        "description": "Management, consulting and public relations",
    },
    "7393": {
        "category": "Detective / Guard / Security Services",
        "description": "Detective agencies and protective services",
    },
    "7394": {
        "category": "Equipment Rental / Leasing",
        "description": "Equipment rental and leasing services",
    },
    "7395": {
        "category": "Photofinishing Laboratories",
        "description": "Photofinishing laboratories and photo developing",
    },
    "7399": {
        "category": "Business Services (Misc)",
        "description": "Business services not elsewhere classified",
    },
    "8111": {
        "category": "Legal Services / Attorneys",
        "description": "Legal services and attorneys",
    },
    "8931": {
        "category": "Accounting / Bookkeeping",
        "description": "Accounting, auditing and bookkeeping services",
    },
    "8999": {
        "category": "Professional Services (Misc)",
        "description": "Services not elsewhere classified",
    },
    # Telecom / Utilities
    "4812": {
        "category": "Telecom Equipment / Phone Stores",
        "description": "Telephone and telecommunication equipment",
    },
    "4813": {
        "category": "Telecom Services",
        "description": "Telephone services — local and long distance",
    },
    "4814": {
        "category": "Telecom Services (Fax / Phone)",
        "description": "Fax services and telephone communications",
    },
    "4816": {
        "category": "Computer Network / Information Services",
        "description": "Computer network and information services",
    },
    "4899": {
        "category": "Cable / Other Pay Television",
        "description": "Cable, satellite and other pay television",
    },
    "4900": {
        "category": "Utilities — Electric / Gas / Water",
        "description": "Electric, gas, water and sanitary services",
    },
    # Transport / Logistics
    "4111": {
        "category": "Local / Suburban Commuter Transport",
        "description": "Local and suburban commuter transport",
    },
    "4112": {
        "category": "Passenger Railways",
        "description": "Passenger railways and rail transport",
    },
    "4119": {"category": "Ambulance Services", "description": "Ambulance services"},
    "4121": {
        "category": "Taxicabs / Limousines",
        "description": "Taxicabs and limousines",
    },
    "4131": {"category": "Bus Lines", "description": "Bus lines"},
    "4214": {
        "category": "Motor Freight Carriers / Trucking",
        "description": "Motor freight carriers and trucking",
    },
    "4215": {
        "category": "Courier Services",
        "description": "Courier services — air and ground",
    },
    "4225": {
        "category": "Public Warehousing / Storage",
        "description": "Public warehousing and storage",
    },
    "4411": {"category": "Cruise Lines", "description": "Cruise lines"},
    "4457": {
        "category": "Boat Rentals / Leases",
        "description": "Boat rentals and leases",
    },
    # Misc Retail
    "5310": {
        "category": "Discount Stores",
        "description": "Discount stores and mega stores",
    },
    "5311": {"category": "Department Stores", "description": "Department stores"},
    "5331": {"category": "Variety Stores", "description": "Variety stores"},
    "5399": {
        "category": "General Merchandise Stores",
        "description": "Miscellaneous general merchandise stores",
    },
    "5900": {
        "category": "Retail Stores (Misc)",
        "description": "Retail stores not elsewhere classified",
    },
    "5999": {
        "category": "Misc Retail Stores",
        "description": "Miscellaneous and specialty retail stores",
    },
    # Personal Services
    "7210": {
        "category": "Laundry / Dry Cleaning",
        "description": "Laundry, cleaning and garment services",
    },
    "7211": {
        "category": "Laundry Services (Family / Commercial)",
        "description": "Laundry services",
    },
    "7216": {"category": "Dry Cleaning", "description": "Dry cleaners"},
    "7217": {
        "category": "Carpet / Upholstery Cleaning",
        "description": "Carpet and upholstery cleaning",
    },
    "7221": {
        "category": "Photographic Studios / Portrait",
        "description": "Photographic studios",
    },
    "7230": {
        "category": "Barber / Beauty Shops",
        "description": "Barber and beauty shops",
    },
    "7251": {
        "category": "Shoe Repair / Shine",
        "description": "Shoe repair, shoe shine parlours",
    },
    "7261": {
        "category": "Funeral Services",
        "description": "Funeral services and crematories",
    },
    "7273": {
        "category": "Dating / Escort Services",
        "description": "Dating and escort services",
    },
    "7276": {
        "category": "Tax Preparation Services",
        "description": "Tax preparation services",
    },
    "7277": {
        "category": "Counselling Services",
        "description": "Counselling services — debt, marriage",
    },
    "7278": {
        "category": "Buying / Shopping Clubs",
        "description": "Buying and shopping services",
    },
    "7296": {
        "category": "Clothing Rental",
        "description": "Clothing rental — costumes, uniforms, formal wear",
    },
    "7297": {"category": "Massage Parlours", "description": "Massage parlours"},
    "7298": {
        "category": "Health / Beauty Spas",
        "description": "Health and beauty spas",
    },
    "7299": {
        "category": "Personal Services (Misc)",
        "description": "Miscellaneous personal services",
    },
    # Subscription / SaaS
    "7375": {
        "category": "Software / SaaS",
        "description": "Prepackaged software — SaaS and subscription services",
    },
}


def format_for_prompt() -> str:
    """Return MCC list formatted for Claude prompt injection."""
    lines = []
    for code, info in sorted(MCC_CODES.items()):
        lines.append(f"{code}: {info['category']} — {info['description']}")
    return "\n".join(lines)
