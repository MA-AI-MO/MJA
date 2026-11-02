window.REVIEW_APP_CONFIG = {
  "businessOrder": [
    "copart",
    "iaa",
    "manheim",
    "adesa",
    "openlane",
    "acv",
    "americas_auto_auction"
  ],
  "businesses": {
    "copart": {
      "display_name": "Copart",
      "switch_label": "Copart",
      "title": "Copart Web Sentiment Analysis Tool",
      "logo_src": "assets/copart-logo.svg",
      "logo_alt": "Copart logo",
      "csv_prefix": "copart",
      "theme": {
        "brand_primary": "#002d4b",
        "brand_secondary": "#1b75bb",
        "title_shade": "#2661d9",
        "negative_line": "#1b75bb",
        "positive_line": "#1b75bb",
        "header_start": "#1f56cb",
        "header_end": "#3f75e6",
        "page_accent_a": "rgba(27, 117, 187, 0.12)",
        "page_accent_b": "rgba(163, 30, 34, 0.08)"
      },
      "output_json": "reviews.json"
    },
    "iaa": {
      "display_name": "IAA",
      "switch_label": "IAA",
      "title": "IAA Web Sentiment Analysis Tool",
      "logo_src": "assets/iaa-logo.png",
      "logo_alt": "IAA logo",
      "csv_prefix": "iaa",
      "theme": {
        "brand_primary": "#1a1d24",
        "brand_secondary": "#cc202f",
        "title_shade": "#cc202f",
        "negative_line": "#cc202f",
        "positive_line": "#cc202f",
        "header_start": "#111319",
        "header_end": "#cc202f",
        "page_accent_a": "rgba(204, 32, 47, 0.12)",
        "page_accent_b": "rgba(31, 35, 44, 0.12)"
      },
      "output_json": "reviews-iaa.json"
    },
    "manheim": {
      "display_name": "Manheim",
      "switch_label": "Manheim",
      "title": "Manheim Web Sentiment Analysis Tool",
      "logo_src": "assets/manheim-logo.svg",
      "logo_alt": "Manheim logo",
      "csv_prefix": "manheim",
      "theme": {
        "brand_primary": "#16324f",
        "brand_secondary": "#f47b20",
        "title_shade": "#f47b20",
        "negative_line": "#f47b20",
        "positive_line": "#f47b20",
        "header_start": "#10273e",
        "header_end": "#f47b20",
        "page_accent_a": "rgba(244, 123, 32, 0.12)",
        "page_accent_b": "rgba(22, 50, 79, 0.10)"
      },
      "output_json": "reviews-manheim.json"
    },
    "adesa": {
      "display_name": "ADESA",
      "switch_label": "ADESA",
      "title": "ADESA Web Sentiment Analysis Tool",
      "logo_src": "assets/adesa-logo.svg",
      "logo_alt": "ADESA logo",
      "csv_prefix": "adesa",
      "theme": {
        "brand_primary": "#183a5a",
        "brand_secondary": "#00a8b5",
        "title_shade": "#00a8b5",
        "negative_line": "#00a8b5",
        "positive_line": "#00a8b5",
        "header_start": "#112b43",
        "header_end": "#00a8b5",
        "page_accent_a": "rgba(0, 168, 181, 0.12)",
        "page_accent_b": "rgba(24, 58, 90, 0.10)"
      },
      "output_json": "reviews-adesa.json"
    },
    "openlane": {
      "display_name": "OPENLANE",
      "switch_label": "OPENLANE",
      "title": "OPENLANE Web Sentiment Analysis Tool",
      "logo_src": "assets/openlane-logo.svg",
      "logo_alt": "OPENLANE logo",
      "csv_prefix": "openlane",
      "theme": {
        "brand_primary": "#1d3f45",
        "brand_secondary": "#00a88e",
        "title_shade": "#00a88e",
        "negative_line": "#00a88e",
        "positive_line": "#00a88e",
        "header_start": "#143137",
        "header_end": "#00a88e",
        "page_accent_a": "rgba(0, 168, 142, 0.12)",
        "page_accent_b": "rgba(29, 63, 69, 0.10)"
      },
      "output_json": "reviews-openlane.json"
    },
    "acv": {
      "display_name": "ACV",
      "switch_label": "ACV",
      "title": "ACV Web Sentiment Analysis Tool",
      "logo_src": "assets/acv-logo.svg",
      "logo_alt": "ACV logo",
      "csv_prefix": "acv",
      "theme": {
        "brand_primary": "#044f7b",
        "brand_secondary": "#00a6d6",
        "title_shade": "#00a6d6",
        "negative_line": "#00a6d6",
        "positive_line": "#00a6d6",
        "header_start": "#043a5a",
        "header_end": "#00a6d6",
        "page_accent_a": "rgba(0, 166, 214, 0.12)",
        "page_accent_b": "rgba(4, 79, 123, 0.10)"
      },
      "output_json": "reviews-acv.json"
    },
    "americas_auto_auction": {
      "display_name": "America's Auto Auction",
      "switch_label": "America's Auto Auction",
      "title": "America's Auto Auction Web Sentiment Analysis Tool",
      "logo_src": "assets/americas-auto-auction-logo.svg",
      "logo_alt": "America's Auto Auction logo",
      "csv_prefix": "americas-auto-auction",
      "theme": {
        "brand_primary": "#1f4d8b",
        "brand_secondary": "#c1272d",
        "title_shade": "#c1272d",
        "negative_line": "#c1272d",
        "positive_line": "#c1272d",
        "header_start": "#183b6a",
        "header_end": "#c1272d",
        "page_accent_a": "rgba(193, 39, 45, 0.12)",
        "page_accent_b": "rgba(31, 77, 139, 0.10)"
      },
      "output_json": "reviews-americas-auto-auction.json"
    }
  },
  "tierHierarchy": {
    "meta": {
      "source": "Business Tiers.xlsx + user-approved custom tiers",
      "tier1_count": 8,
      "allowed_path_count": 112,
      "custom_tier1_added": [
        "Customer Service & Communication"
      ]
    },
    "hierarchy": {
      "Lot Condition, Listing Status and related": {
        "Lot Condition Reporting": [
          "Lot Damage"
        ],
        "Third-Party Inspection Authorization & Scheduling": [
          "Previewing/ Inspecting Vehicles"
        ],
        "Listing Status": [
          "Selling/ Relisting vehicle or Parts purchase",
          "Lot Cancellation/Closure & Reassignment"
        ],
        "Personal belongings/ items": [
          "Removal / Retrieval of items left in vehicle"
        ]
      },
      "Title, Ownership, POA and Documentation": {
        "Duplicate Title Processing": [
          "Duplicate Title Application & Request",
          "Duplicate Title Status",
          "Duplicate Title via Yard"
        ],
        "Power of Attorney (POA) Handling": [
          "POA Completion & Notary",
          "POA Rejected-Fix & Resubmit",
          "POA Requirements Clarification",
          "POA Setup & Address"
        ],
        "Title Delivery & Status": [
          "Single/ Multiple Vehicle Title Status",
          "Title Not Received",
          "Title Pickup or Driver Handoff"
        ],
        "Title Dept Routing": [
          "Insurance Claim Title Coordination",
          "Transfer to Correct Dept",
          "Transfer to Title Express"
        ],
        "Title Paperwork & Corrections": [
          "Lien Release Processing",
          "Title Corrections/Affidavits"
        ]
      },
      "Vehicle Pickup, Delivery and Scheduling": {
        "Delivery Coordination & Handoffs": [
          "Delivery Location Update",
          "Key Handoff Issues",
          "License Plate Retrieval",
          "Delivery Status and ETA"
        ],
        "Dispatch Routing & Support": [
          "App Guidance and Callback",
          "Transfer to Dispatch"
        ],
        "Pickup Order Management": [
          "Gate Pass Assistance",
          "3-Way Scheduling",
          "Pickup Status/Holds",
          "Insurance Lot Coordination & Owner-Retain/Release"
        ],
        "Scheduled Pickup Status": [
          "Missed/ Delayed Pickup and Dispatch Window",
          "Pickup Hours and Cutoff",
          "Schedule/ Reschedule Pickup"
        ],
        "Specialty Unit Pickups": [
          "Jet Ski Pickup",
          "RV or Camper Pickup",
          "Trailer or Boat Pickup"
        ],
        "Tow and Storage Charges": [
          "Storage Fee Waiver",
          "Tow and Storage Fees",
          "Tow Charge Approval"
        ],
        "Towing Network & Dispatch": [
          "Tow Company Contact",
          "Tow Dispatch & Requests",
          "Tow Provider Onboarding"
        ]
      },
      "Membership / Licensing / Fees & Bidding Policies": {
        "Account Suspension & Reactivation": [
          "Suspended-Duplicate/Access",
          "Suspended-Docs/Deposit",
          "Account Suspended – Payment",
          "Suspended-Pending Review/ Verification"
        ],
        "Auction Eligibility & Licensing": [
          "Auction Eligibility Overview",
          "Dealer Account Setup",
          "State-Specific Bidding Restrictions/ Guide",
          "Unable to Bid"
        ],
        "Bidding Limits & Buying Power": [
          "Buy/Bid Limits Reached",
          "Buying Power",
          "Increase ePay Limit"
        ],
        "Bidding Process, Rules and Fees": [
          "Bid Approval Timeline",
          "Bid Cancellation & Relist Fees",
          "Bid Status and Disputes",
          "Bidding Limits & Restrictions",
          "Fees",
          "How to Bid (First Time)",
          "Membership Types & Licensing Overview"
        ],
        "Membership Status & Deposits": [
          "Inactive Membership- Address Update",
          "Inactive Membership- Renewal",
          "Membership/Deposit Status Inquiry"
        ]
      },
      "Account / Access / Login": {
        "Account Access Issues": [
          "Account Locked",
          "Unable to sign in"
        ],
        "Account Info & Visitor Access": [
          "Add Visitor Access",
          "General Account Information"
        ],
        "Account Profile Updates": [
          "Account Details Update",
          "Update/ Change mailing Address"
        ],
        "Cardholder & Bidder Management": [
          "Add Cardholder/Bidder"
        ],
        "Dealer/Seller Account Setup & Activation": [
          "Create Seller Account",
          "Dealer Services Registration",
          "Dealer/Seller Routing & Activation"
        ],
        "Document Upload & Verification": [
          "Affidavit & Resale Forms",
          "Document Status Update",
          "Inactive Account",
          "Licensing Documents Verification",
          "Upload Troubleshooting"
        ],
        "Password Reset & Login Troubleshooting": [
          "App Login Troubleshooting",
          "Password Reset & Email Update"
        ]
      },
      "Payment Refunds, Transaction Issues and Deposits": {
        "Fees & Charges Disputes": [
          "Buyer Fees Explanation",
          "Relist Fee Dispute",
          "Storage Fees Dispute"
        ],
        "Payment Methods & Limits": [
          "Card Payment Declined",
          "Debit Payment Discounts",
          "Payment Deadlines & Rules",
          "Types of Accepted Payment Methods"
        ],
        "Post-Sale Payment & Counteroffers": [
          "Not Received Payment post vehicle pickup",
          "Counteroffer & Fees Questions",
          "Payment Rejected"
        ],
        "Refunds & Membership Billing": [
          "Deposit Refund & Closure",
          "Deposit Refund Status",
          "Membership Refund – Apple Pay",
          "Membership Refund – Ineligible to bid",
          "Membership Renewal Billing"
        ],
        "Wire Transfer Payments": [
          "Wire Not Received – Info Error",
          "Wire Pending/Posting Delay",
          "Wire Rejected – Name Mismatch"
        ]
      },
      "Misc / General Inquiry": {
        "Unintelligible/No Conversation": [
          "-"
        ],
        "Find Directions to Yard/ Connect to Yard": [
          "Yard Directions/ Yard Employee Availability etc."
        ],
        "Support/Routing": [
          "Language Assistance"
        ],
        "Inventory & Listing Inquiries": [
          "Vehicle Availability Inquiry, Listing Missing/Not Posted, Pickup Arrival/Status"
        ]
      },
      "Customer Service & Communication": {
        "Agent Professionalism & Responsiveness": [
          "Rude/Unhelpful Support",
          "Helpful Support Experience"
        ],
        "Communication Follow-up & Escalation": [
          "No Callback / Unresolved Case",
          "Proactive Follow-up"
        ],
        "Support Access & Response Time": [
          "Long Hold Time / Hard to Reach Support",
          "Delayed Email/Phone Response",
          "Quick Support Response"
        ],
        "Case Resolution Quality": [
          "Issue Not Resolved",
          "Issue Resolved",
          "Escalation Required"
        ]
      }
    },
    "allowed_paths": [
      {
        "tier1": "Account / Access / Login",
        "tier2": "Account Access Issues",
        "tier3": "Account Locked"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Account Access Issues",
        "tier3": "Unable to sign in"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Account Info & Visitor Access",
        "tier3": "Add Visitor Access"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Account Info & Visitor Access",
        "tier3": "General Account Information"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Account Profile Updates",
        "tier3": "Account Details Update"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Account Profile Updates",
        "tier3": "Update/ Change mailing Address"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Cardholder & Bidder Management",
        "tier3": "Add Cardholder/Bidder"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Dealer/Seller Account Setup & Activation",
        "tier3": "Create Seller Account"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Dealer/Seller Account Setup & Activation",
        "tier3": "Dealer Services Registration"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Dealer/Seller Account Setup & Activation",
        "tier3": "Dealer/Seller Routing & Activation"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Document Upload & Verification",
        "tier3": "Affidavit & Resale Forms"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Document Upload & Verification",
        "tier3": "Document Status Update"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Document Upload & Verification",
        "tier3": "Inactive Account"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Document Upload & Verification",
        "tier3": "Licensing Documents Verification"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Document Upload & Verification",
        "tier3": "Upload Troubleshooting"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Password Reset & Login Troubleshooting",
        "tier3": "App Login Troubleshooting"
      },
      {
        "tier1": "Account / Access / Login",
        "tier2": "Password Reset & Login Troubleshooting",
        "tier3": "Password Reset & Email Update"
      },
      {
        "tier1": "Customer Service & Communication",
        "tier2": "Agent Professionalism & Responsiveness",
        "tier3": "Helpful Support Experience"
      },
      {
        "tier1": "Customer Service & Communication",
        "tier2": "Agent Professionalism & Responsiveness",
        "tier3": "Rude/Unhelpful Support"
      },
      {
        "tier1": "Customer Service & Communication",
        "tier2": "Case Resolution Quality",
        "tier3": "Escalation Required"
      },
      {
        "tier1": "Customer Service & Communication",
        "tier2": "Case Resolution Quality",
        "tier3": "Issue Not Resolved"
      },
      {
        "tier1": "Customer Service & Communication",
        "tier2": "Case Resolution Quality",
        "tier3": "Issue Resolved"
      },
      {
        "tier1": "Customer Service & Communication",
        "tier2": "Communication Follow-up & Escalation",
        "tier3": "No Callback / Unresolved Case"
      },
      {
        "tier1": "Customer Service & Communication",
        "tier2": "Communication Follow-up & Escalation",
        "tier3": "Proactive Follow-up"
      },
      {
        "tier1": "Customer Service & Communication",
        "tier2": "Support Access & Response Time",
        "tier3": "Delayed Email/Phone Response"
      },
      {
        "tier1": "Customer Service & Communication",
        "tier2": "Support Access & Response Time",
        "tier3": "Long Hold Time / Hard to Reach Support"
      },
      {
        "tier1": "Customer Service & Communication",
        "tier2": "Support Access & Response Time",
        "tier3": "Quick Support Response"
      },
      {
        "tier1": "Lot Condition, Listing Status and related",
        "tier2": "Listing Status",
        "tier3": "Lot Cancellation/Closure & Reassignment"
      },
      {
        "tier1": "Lot Condition, Listing Status and related",
        "tier2": "Listing Status",
        "tier3": "Selling/ Relisting vehicle or Parts purchase"
      },
      {
        "tier1": "Lot Condition, Listing Status and related",
        "tier2": "Lot Condition Reporting",
        "tier3": "Lot Damage"
      },
      {
        "tier1": "Lot Condition, Listing Status and related",
        "tier2": "Personal belongings/ items",
        "tier3": "Removal / Retrieval of items left in vehicle"
      },
      {
        "tier1": "Lot Condition, Listing Status and related",
        "tier2": "Third-Party Inspection Authorization & Scheduling",
        "tier3": "Previewing/ Inspecting Vehicles"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Account Suspension & Reactivation",
        "tier3": "Account Suspended – Payment"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Account Suspension & Reactivation",
        "tier3": "Suspended-Docs/Deposit"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Account Suspension & Reactivation",
        "tier3": "Suspended-Duplicate/Access"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Account Suspension & Reactivation",
        "tier3": "Suspended-Pending Review/ Verification"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Auction Eligibility & Licensing",
        "tier3": "Auction Eligibility Overview"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Auction Eligibility & Licensing",
        "tier3": "Dealer Account Setup"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Auction Eligibility & Licensing",
        "tier3": "State-Specific Bidding Restrictions/ Guide"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Auction Eligibility & Licensing",
        "tier3": "Unable to Bid"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Bidding Limits & Buying Power",
        "tier3": "Buy/Bid Limits Reached"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Bidding Limits & Buying Power",
        "tier3": "Buying Power"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Bidding Limits & Buying Power",
        "tier3": "Increase ePay Limit"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Bidding Process, Rules and Fees",
        "tier3": "Bid Approval Timeline"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Bidding Process, Rules and Fees",
        "tier3": "Bid Cancellation & Relist Fees"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Bidding Process, Rules and Fees",
        "tier3": "Bid Status and Disputes"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Bidding Process, Rules and Fees",
        "tier3": "Bidding Limits & Restrictions"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Bidding Process, Rules and Fees",
        "tier3": "Fees"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Bidding Process, Rules and Fees",
        "tier3": "How to Bid (First Time)"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Bidding Process, Rules and Fees",
        "tier3": "Membership Types & Licensing Overview"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Membership Status & Deposits",
        "tier3": "Inactive Membership- Address Update"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Membership Status & Deposits",
        "tier3": "Inactive Membership- Renewal"
      },
      {
        "tier1": "Membership / Licensing / Fees & Bidding Policies",
        "tier2": "Membership Status & Deposits",
        "tier3": "Membership/Deposit Status Inquiry"
      },
      {
        "tier1": "Misc / General Inquiry",
        "tier2": "Find Directions to Yard/ Connect to Yard",
        "tier3": "Yard Directions/ Yard Employee Availability etc."
      },
      {
        "tier1": "Misc / General Inquiry",
        "tier2": "Inventory & Listing Inquiries",
        "tier3": "Vehicle Availability Inquiry, Listing Missing/Not Posted, Pickup Arrival/Status"
      },
      {
        "tier1": "Misc / General Inquiry",
        "tier2": "Support/Routing",
        "tier3": "Language Assistance"
      },
      {
        "tier1": "Misc / General Inquiry",
        "tier2": "Unintelligible/No Conversation",
        "tier3": "-"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Fees & Charges Disputes",
        "tier3": "Buyer Fees Explanation"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Fees & Charges Disputes",
        "tier3": "Relist Fee Dispute"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Fees & Charges Disputes",
        "tier3": "Storage Fees Dispute"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Payment Methods & Limits",
        "tier3": "Card Payment Declined"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Payment Methods & Limits",
        "tier3": "Debit Payment Discounts"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Payment Methods & Limits",
        "tier3": "Payment Deadlines & Rules"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Payment Methods & Limits",
        "tier3": "Types of Accepted Payment Methods"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Post-Sale Payment & Counteroffers",
        "tier3": "Counteroffer & Fees Questions"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Post-Sale Payment & Counteroffers",
        "tier3": "Not Received Payment post vehicle pickup"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Post-Sale Payment & Counteroffers",
        "tier3": "Payment Rejected"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Refunds & Membership Billing",
        "tier3": "Deposit Refund & Closure"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Refunds & Membership Billing",
        "tier3": "Deposit Refund Status"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Refunds & Membership Billing",
        "tier3": "Membership Refund – Apple Pay"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Refunds & Membership Billing",
        "tier3": "Membership Refund – Ineligible to bid"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Refunds & Membership Billing",
        "tier3": "Membership Renewal Billing"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Wire Transfer Payments",
        "tier3": "Wire Not Received – Info Error"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Wire Transfer Payments",
        "tier3": "Wire Pending/Posting Delay"
      },
      {
        "tier1": "Payment Refunds, Transaction Issues and Deposits",
        "tier2": "Wire Transfer Payments",
        "tier3": "Wire Rejected – Name Mismatch"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Duplicate Title Processing",
        "tier3": "Duplicate Title Application & Request"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Duplicate Title Processing",
        "tier3": "Duplicate Title Status"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Duplicate Title Processing",
        "tier3": "Duplicate Title via Yard"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Power of Attorney (POA) Handling",
        "tier3": "POA Completion & Notary"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Power of Attorney (POA) Handling",
        "tier3": "POA Rejected-Fix & Resubmit"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Power of Attorney (POA) Handling",
        "tier3": "POA Requirements Clarification"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Power of Attorney (POA) Handling",
        "tier3": "POA Setup & Address"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Title Delivery & Status",
        "tier3": "Single/ Multiple Vehicle Title Status"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Title Delivery & Status",
        "tier3": "Title Not Received"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Title Delivery & Status",
        "tier3": "Title Pickup or Driver Handoff"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Title Dept Routing",
        "tier3": "Insurance Claim Title Coordination"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Title Dept Routing",
        "tier3": "Transfer to Correct Dept"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Title Dept Routing",
        "tier3": "Transfer to Title Express"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Title Paperwork & Corrections",
        "tier3": "Lien Release Processing"
      },
      {
        "tier1": "Title, Ownership, POA and Documentation",
        "tier2": "Title Paperwork & Corrections",
        "tier3": "Title Corrections/Affidavits"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Delivery Coordination & Handoffs",
        "tier3": "Delivery Location Update"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Delivery Coordination & Handoffs",
        "tier3": "Delivery Status and ETA"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Delivery Coordination & Handoffs",
        "tier3": "Key Handoff Issues"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Delivery Coordination & Handoffs",
        "tier3": "License Plate Retrieval"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Dispatch Routing & Support",
        "tier3": "App Guidance and Callback"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Dispatch Routing & Support",
        "tier3": "Transfer to Dispatch"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Pickup Order Management",
        "tier3": "3-Way Scheduling"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Pickup Order Management",
        "tier3": "Gate Pass Assistance"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Pickup Order Management",
        "tier3": "Insurance Lot Coordination & Owner-Retain/Release"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Pickup Order Management",
        "tier3": "Pickup Status/Holds"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Scheduled Pickup Status",
        "tier3": "Missed/ Delayed Pickup and Dispatch Window"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Scheduled Pickup Status",
        "tier3": "Pickup Hours and Cutoff"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Scheduled Pickup Status",
        "tier3": "Schedule/ Reschedule Pickup"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Specialty Unit Pickups",
        "tier3": "Jet Ski Pickup"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Specialty Unit Pickups",
        "tier3": "RV or Camper Pickup"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Specialty Unit Pickups",
        "tier3": "Trailer or Boat Pickup"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Tow and Storage Charges",
        "tier3": "Storage Fee Waiver"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Tow and Storage Charges",
        "tier3": "Tow Charge Approval"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Tow and Storage Charges",
        "tier3": "Tow and Storage Fees"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Towing Network & Dispatch",
        "tier3": "Tow Company Contact"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Towing Network & Dispatch",
        "tier3": "Tow Dispatch & Requests"
      },
      {
        "tier1": "Vehicle Pickup, Delivery and Scheduling",
        "tier2": "Towing Network & Dispatch",
        "tier3": "Tow Provider Onboarding"
      }
    ]
  },
  "coverageNote": {
    "generated_at": "2026-11-02T21:33:05.549876Z",
    "target_since": "2023-01-01",
    "target_until": "2026-10-31",
    "refreshed": [
      {
        "key": "copart",
        "display_name": "Copart",
        "until_date": "2026-10-31",
        "since_date": "2023-01-01",
        "review_count": 13510,
        "source_counts": {
          "reddit.com": 6871,
          "play.google.com": 690,
          "apps.apple.com": 276,
          "trustpilot.com": 268,
          "google.com": 4224,
          "bbb.org": 941,
          "reviews.io": 225,
          "complaintsboard.com": 15
        },
        "source_audit": [
          {
            "source_website": "reddit.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 129,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "reddit_pullpush ran; candidate count is not separately tracked for this collector.",
              "reddit_arctic_shift ran; candidate count is not separately tracked for this collector."
            ],
            "errors": [],
            "review_count": 6871,
            "existing_review_count": 6742,
            "present": true,
            "latest_review_date": "2026-10-31",
            "existing_latest_date": "2026-09-30",
            "status": "ok"
          },
          {
            "source_website": "play.google.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 4140,
            "new_reviews_added": 14,
            "advertised_total": null,
            "latest_candidate_date": "2026-11-01",
            "notes": [],
            "errors": [],
            "review_count": 690,
            "existing_review_count": 676,
            "present": true,
            "latest_review_date": "2026-10-30",
            "existing_latest_date": "2026-09-30",
            "status": "ok"
          },
          {
            "source_website": "apps.apple.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 717,
            "new_reviews_added": 7,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-28",
            "notes": [
              "Apple RSS can be sparse for some app IDs; HTML supplement captures visible App Store review cards only."
            ],
            "errors": [],
            "review_count": 276,
            "existing_review_count": 269,
            "present": true,
            "latest_review_date": "2026-10-26",
            "existing_latest_date": "2026-09-30",
            "status": "ok"
          },
          {
            "source_website": "bbb.org",
            "attempted": true,
            "direct_pages": 2,
            "fallback_pages": 1,
            "direct_statuses": {
              "403": 2,
              "200": 1
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "direct BBB customer reviews blocked for https://www.bbb.org/us/tx/dallas/profile/online-car-dealers/copart-inc-0875-90403032",
              "direct BBB complaints blocked for https://www.bbb.org/us/tx/dallas/profile/online-car-dealers/copart-inc-0875-90403032",
              "reader challenge for https://www.bbb.org/us/tx/dallas/profile/online-car-dealers/copart-inc-0875-90403032/complaints"
            ],
            "errors": [
              "reader error for https://www.bbb.org/us/tx/dallas/profile/online-car-dealers/copart-inc-0875-90403032/customer-reviews: HTTPSConnectionPool(host='r.jina.ai', port=443): Read timed out. (read timeout=60)"
            ],
            "review_count": 941,
            "existing_review_count": 941,
            "present": true,
            "latest_review_date": "2026-09-23",
            "existing_latest_date": "2026-09-23",
            "status": "stale_or_no_recent_candidates"
          },
          {
            "source_website": "trustpilot.com",
            "attempted": true,
            "direct_pages": 9,
            "fallback_pages": 31,
            "direct_statuses": {
              "403": 9,
              "200": 31
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 421,
            "new_reviews_added": 5,
            "advertised_total": null,
            "latest_candidate_date": "2026-11-02",
            "notes": [
              "direct Trustpilot blocked for copart.co.uk",
              "reader challenge for https://www.trustpilot.com/review/copart.co.uk?page=11",
              "direct Trustpilot blocked for copart.com",
              "reader challenge for https://www.trustpilot.com/review/copart.com?page=11",
              "direct Trustpilot blocked for copart.de",
              "direct Trustpilot blocked for copart.ie",
              "reader challenge for https://www.trustpilot.com/review/copart.ie",
              "direct Trustpilot blocked for copart.es",
              "reader challenge for https://www.trustpilot.com/review/copart.es",
              "direct Trustpilot blocked for copart.fr",
              "reader challenge for https://www.trustpilot.com/review/copart.fr",
              "direct Trustpilot blocked for copart.nl",
              "reader challenge for https://www.trustpilot.com/review/copart.nl",
              "direct Trustpilot blocked for copart.it",
              "reader challenge for https://www.trustpilot.com/review/copart.it",
              "direct Trustpilot blocked for copart.ca",
              "reader challenge for https://www.trustpilot.com/review/copart.ca"
            ],
            "errors": [],
            "review_count": 268,
            "existing_review_count": 263,
            "present": true,
            "latest_review_date": "2026-10-14",
            "existing_latest_date": "2026-09-25",
            "status": "ok"
          },
          {
            "source_website": "reviews.io",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 0,
            "direct_statuses": {
              "403": 1
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [],
            "errors": [],
            "review_count": 225,
            "existing_review_count": 225,
            "present": true,
            "latest_review_date": "2026-02-19",
            "existing_latest_date": "2026-02-19",
            "status": "stale_or_no_recent_candidates"
          },
          {
            "source_website": "ripoffreport.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "ripoffreport ran; candidate count is not separately tracked for this collector."
            ],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "missing"
          },
          {
            "source_website": "smartcustomer.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 1
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 2,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "parsed_no_new_rows"
          },
          {
            "source_website": "complaintsboard.com",
            "attempted": true,
            "direct_pages": 6,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 6
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 113,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2024-02-14",
            "notes": [],
            "errors": [],
            "review_count": 15,
            "existing_review_count": 15,
            "present": true,
            "latest_review_date": "2023-11-03",
            "existing_latest_date": "2023-11-03",
            "status": "ok"
          },
          {
            "source_website": "google.com",
            "attempted": true,
            "direct_pages": 170,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 170
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 18,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2026-08-19",
            "notes": [
              "Google Business Profile discovery completed: 67/67 queries succeeded and 216 unique validated US profiles were selected.",
              "Validated 5 US Google Business Profiles; 11 failed and 200 were skipped after the circuit breaker. Successful profiles were paginated newest-first through per-profile incremental overlap boundaries."
            ],
            "errors": [
              "[CLOSED] Copart - Jacksonville East [0x88e5ba1f49465365:0xc436311ceac59ef7]: newest review RPC did not load",
              "[CLOSED] Copart - Punta Gorda [0x88dca771d7def04b:0xee95a25a94e7c802]: Response.body: Protocol error (Network.getResponseBody): No data found for resource with given identifier\nResponse body is not available for a response that was navigated away from. Read response.body() before triggering any navi",
              "[CLOSED] Copart - Salt Lake City North [0x8752f6e2e313caa9:0xab631f805c05d36f]: newest review RPC did not load",
              "Copart [0x88626986bd637fd5:0x330ba218453c6021]: newest review RPC did not load",
              "Copart [0x52b33121975753cf:0x22834afe7b18657e]: newest review RPC did not load",
              "Copart [0x80c25341a6543b5f:0xf29e32dc4dcf394a]: newest review RPC did not load",
              "Copart - Abilene [0x8656855e69478b1b:0xd9b0d6e36022a489]: newest review RPC did not load",
              "Copart - Adelanto [0x80c36fd137accac5:0xff177c73ccf09e13]: newest review RPC did not load",
              "Copart - Akron [0x8830d3c9f287f237:0x8765346cae4762f3]: newest review RPC did not load",
              "Copart - Albany [0x89de7347839bfbd7:0x2f00025f0c2262a0]: newest review RPC did not load",
              "Copart - Albuquerque [0x87220ee934b2ba93:0x6edfdefbd5fe27c]: newest review RPC did not load"
            ],
            "profile_retention_used": true,
            "profiles_completed": 5,
            "profiles_failed": 11,
            "profiles_skipped_after_circuit_breaker": 200,
            "last_successful_refresh_until": "2026-08-31",
            "review_count": 4224,
            "existing_review_count": 4224,
            "present": true,
            "latest_review_date": "2026-09-30",
            "existing_latest_date": "2026-09-30",
            "status": "partial_profile_retention"
          }
        ]
      },
      {
        "key": "iaa",
        "display_name": "IAA",
        "until_date": "2026-10-31",
        "since_date": "2023-01-01",
        "review_count": 4696,
        "source_counts": {
          "trustpilot.com": 94,
          "play.google.com": 258,
          "apps.apple.com": 156,
          "google.com": 2364,
          "bbb.org": 817,
          "reddit.com": 1004,
          "complaintsboard.com": 3
        },
        "source_audit": [
          {
            "source_website": "reddit.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 1,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "reddit_pullpush ran; candidate count is not separately tracked for this collector.",
              "reddit_arctic_shift ran; candidate count is not separately tracked for this collector."
            ],
            "errors": [],
            "review_count": 1004,
            "existing_review_count": 1003,
            "present": true,
            "latest_review_date": "2026-09-16",
            "existing_latest_date": "2026-07-30",
            "status": "ok"
          },
          {
            "source_website": "play.google.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 1363,
            "new_reviews_added": 6,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-30",
            "notes": [],
            "errors": [],
            "review_count": 258,
            "existing_review_count": 252,
            "present": true,
            "latest_review_date": "2026-10-23",
            "existing_latest_date": "2026-09-02",
            "status": "ok"
          },
          {
            "source_website": "apps.apple.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 293,
            "new_reviews_added": 4,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-23",
            "notes": [
              "Apple RSS can be sparse for some app IDs; HTML supplement captures visible App Store review cards only."
            ],
            "errors": [],
            "review_count": 156,
            "existing_review_count": 152,
            "present": true,
            "latest_review_date": "2026-10-23",
            "existing_latest_date": "2026-09-16",
            "status": "ok"
          },
          {
            "source_website": "bbb.org",
            "attempted": true,
            "direct_pages": 23,
            "fallback_pages": 23,
            "direct_statuses": {
              "403": 23,
              "200": 23
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 60,
            "new_reviews_added": 47,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-06",
            "notes": [
              "direct BBB customer reviews blocked for https://www.bbb.org/us/az/tucson/profile/auto-auction/iaa-tucson-1286-20009500",
              "reader challenge for https://www.bbb.org/us/az/tucson/profile/auto-auction/iaa-tucson-1286-20009500/customer-reviews",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/fl/jacksonville/profile/auto-auction/iaa-0403-235995143",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/ga/rincon/profile/auto-auction/iaa-0403-235995144",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/il/granite-city/profile/auto-auction/iaa-0734-310253272",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/il/westchester/profile/auto-auction/iaa-0654-88276839",
              "reader challenge for https://www.bbb.org/us/il/westchester/profile/auto-auction/iaa-0654-88276839/customer-reviews?page=6",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/il/westchester/profile/auto-auction/iaa-0654-88276839/details",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/ny/medford/profile/auto-auction/iaa-0121-143499",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/sc/lexington/profile/auto-auction/iaa-0663-34111613",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/sc/ravenel/profile/auto-auction/iaa-0663-34311514",
              "direct BBB complaints blocked for https://www.bbb.org/us/az/tucson/profile/auto-auction/iaa-tucson-1286-20009500",
              "direct BBB complaints blocked for https://www.bbb.org/us/fl/jacksonville/profile/auto-auction/iaa-0403-235995143",
              "direct BBB complaints blocked for https://www.bbb.org/us/ga/rincon/profile/auto-auction/iaa-0403-235995144",
              "direct BBB complaints blocked for https://www.bbb.org/us/il/granite-city/profile/auto-auction/iaa-0734-310253272",
              "direct BBB complaints blocked for https://www.bbb.org/us/il/westchester/profile/auto-auction/iaa-0654-88276839",
              "reader challenge for https://www.bbb.org/us/il/westchester/profile/auto-auction/iaa-0654-88276839/complaints?page=2",
              "direct BBB complaints blocked for https://www.bbb.org/us/il/westchester/profile/auto-auction/iaa-0654-88276839/details",
              "reader challenge for https://www.bbb.org/us/il/westchester/profile/auto-auction/iaa-0654-88276839/details/complaints",
              "direct BBB complaints blocked for https://www.bbb.org/us/ny/medford/profile/auto-auction/iaa-0121-143499",
              "direct BBB complaints blocked for https://www.bbb.org/us/sc/ravenel/profile/auto-auction/iaa-0663-34311514"
            ],
            "errors": [],
            "review_count": 817,
            "existing_review_count": 770,
            "present": true,
            "latest_review_date": "2026-09-24",
            "existing_latest_date": "2026-09-24",
            "status": "ok"
          },
          {
            "source_website": "trustpilot.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 2,
            "direct_statuses": {
              "403": 1,
              "200": 2
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 16,
            "new_reviews_added": 2,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-26",
            "notes": [
              "direct Trustpilot blocked for iaai.com",
              "reader challenge for https://www.trustpilot.com/review/iaai.com?page=2"
            ],
            "errors": [],
            "review_count": 94,
            "existing_review_count": 92,
            "present": true,
            "latest_review_date": "2026-10-26",
            "existing_latest_date": "2026-09-11",
            "status": "ok"
          },
          {
            "source_website": "ripoffreport.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "ripoffreport ran; candidate count is not separately tracked for this collector."
            ],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "missing"
          },
          {
            "source_website": "smartcustomer.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 1
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 1,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "parsed_no_new_rows"
          },
          {
            "source_website": "complaintsboard.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 1
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 30,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2024-02-05",
            "notes": [],
            "errors": [],
            "review_count": 3,
            "existing_review_count": 3,
            "present": true,
            "latest_review_date": "2024-02-05",
            "existing_latest_date": "2024-02-05",
            "status": "ok"
          },
          {
            "source_website": "google.com",
            "attempted": true,
            "direct_pages": 286,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 286
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 8,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2025-10-21",
            "notes": [
              "Google Business Profile discovery completed: 131/131 queries succeeded and 310 unique validated US profiles were selected.",
              "Validated 2 US Google Business Profiles; 6 failed and 302 were skipped after the circuit breaker. Successful profiles were paginated newest-first through per-profile incremental overlap boundaries."
            ],
            "errors": [
              "Auto Auction Insurance [0x8881c58137f61ecd:0xabecba8ed5a95f0c]: Response.body: Protocol error (Network.getResponseBody): No data found for resource with given identifier\nResponse body is not available for a response that was navigated away from. Read response.body() before triggering any navigation.",
              "IAA Abilene [0x8656859fd806721d:0x1c9eadd6f9b8fefa]: newest review RPC did not load",
              "IAA Akron-Canton [0x8836fb149c514035:0x5fd3cb09819cb4cf]: newest review RPC did not load",
              "IAA Albany [0x89de730ae2b661b3:0x9d58bae6b93a9718]: newest review RPC did not load",
              "IAA Albuquerque [0x87220ea7338e1f9d:0x1e3799baac92c395]: newest review RPC did not load",
              "IAA Altoona [0x89cbbcfa7c283bbd:0x82eef90752880501]: newest review RPC did not load"
            ],
            "profile_retention_used": true,
            "profiles_completed": 2,
            "profiles_failed": 6,
            "profiles_skipped_after_circuit_breaker": 302,
            "last_successful_refresh_until": "2026-08-31",
            "review_count": 2364,
            "existing_review_count": 2364,
            "present": true,
            "latest_review_date": "2026-09-30",
            "existing_latest_date": "2026-09-30",
            "status": "partial_profile_retention"
          }
        ]
      },
      {
        "key": "manheim",
        "display_name": "Manheim",
        "until_date": "2026-10-31",
        "since_date": "2023-01-01",
        "review_count": 2252,
        "source_counts": {
          "play.google.com": 96,
          "bbb.org": 298,
          "apps.apple.com": 131,
          "reddit.com": 155,
          "birdeye.com": 81,
          "google.com": 1480,
          "trustpilot.com": 11
        },
        "source_audit": [
          {
            "source_website": "reddit.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 3,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "reddit_pullpush ran; candidate count is not separately tracked for this collector.",
              "reddit_arctic_shift ran; candidate count is not separately tracked for this collector."
            ],
            "errors": [],
            "review_count": 155,
            "existing_review_count": 152,
            "present": true,
            "latest_review_date": "2026-10-22",
            "existing_latest_date": "2026-08-25",
            "status": "ok"
          },
          {
            "source_website": "play.google.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 332,
            "new_reviews_added": 22,
            "advertised_total": null,
            "latest_candidate_date": "2026-11-01",
            "notes": [],
            "errors": [],
            "review_count": 96,
            "existing_review_count": 74,
            "present": true,
            "latest_review_date": "2026-10-29",
            "existing_latest_date": "2026-09-30",
            "status": "ok"
          },
          {
            "source_website": "apps.apple.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 60,
            "new_reviews_added": 12,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-23",
            "notes": [
              "Apple RSS can be sparse for some app IDs; HTML supplement captures visible App Store review cards only."
            ],
            "errors": [],
            "review_count": 131,
            "existing_review_count": 119,
            "present": true,
            "latest_review_date": "2026-10-23",
            "existing_latest_date": "2026-09-30",
            "status": "ok"
          },
          {
            "source_website": "bbb.org",
            "attempted": true,
            "direct_pages": 17,
            "fallback_pages": 17,
            "direct_statuses": {
              "403": 17,
              "200": 17
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 31,
            "new_reviews_added": 9,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-23",
            "notes": [
              "direct BBB customer reviews blocked for https://www.bbb.org/us/az/tolleson/profile/auto-auction/manheim-phoenix-1126-15000273",
              "reader challenge for https://www.bbb.org/us/az/tolleson/profile/auto-auction/manheim-phoenix-1126-15000273/customer-reviews",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/ca/anaheim/profile/auto-auction/manheim-auctions-1126-1000068323",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/fl/tampa/profile/auto-auction/manheim-auctions-0653-90021503",
              "reader challenge for https://www.bbb.org/us/fl/tampa/profile/auto-auction/manheim-auctions-0653-90021503/customer-reviews",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/ga/atlanta/profile/auctioneer/manheim-auctions-0443-6001743",
              "reader challenge for https://www.bbb.org/us/ga/atlanta/profile/auctioneer/manheim-auctions-0443-6001743/customer-reviews?page=2",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/in/indianapolis/profile/auto-auction/manheim-indianapolis-auto-auction-0382-90005341",
              "reader challenge for https://www.bbb.org/us/in/indianapolis/profile/auto-auction/manheim-indianapolis-auto-auction-0382-90005341/customer-reviews",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/mi/carleton/profile/auto-auction/manheims-detroit-auto-auction-0422-6001794",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/pa/manheim/profile/auctioneer/manheim-pennsylvania-auto-auction-0241-184056004",
              "reader challenge for https://www.bbb.org/us/pa/manheim/profile/auctioneer/manheim-pennsylvania-auto-auction-0241-184056004/customer-reviews",
              "direct BBB complaints blocked for https://www.bbb.org/us/az/tolleson/profile/auto-auction/manheim-phoenix-1126-15000273",
              "reader challenge for https://www.bbb.org/us/az/tolleson/profile/auto-auction/manheim-phoenix-1126-15000273/complaints",
              "direct BBB complaints blocked for https://www.bbb.org/us/ca/anaheim/profile/auto-auction/manheim-auctions-1126-1000068323",
              "direct BBB complaints blocked for https://www.bbb.org/us/fl/tampa/profile/auto-auction/manheim-auctions-0653-90021503",
              "direct BBB complaints blocked for https://www.bbb.org/us/ga/atlanta/profile/auctioneer/manheim-auctions-0443-6001743",
              "reader challenge for https://www.bbb.org/us/ga/atlanta/profile/auctioneer/manheim-auctions-0443-6001743/complaints?page=3",
              "direct BBB complaints blocked for https://www.bbb.org/us/in/indianapolis/profile/auto-auction/manheim-indianapolis-auto-auction-0382-90005341",
              "direct BBB complaints blocked for https://www.bbb.org/us/mi/carleton/profile/auto-auction/manheims-detroit-auto-auction-0422-6001794",
              "direct BBB complaints blocked for https://www.bbb.org/us/pa/manheim/profile/auctioneer/manheim-pennsylvania-auto-auction-0241-184056004"
            ],
            "errors": [],
            "review_count": 298,
            "existing_review_count": 289,
            "present": true,
            "latest_review_date": "2026-10-23",
            "existing_latest_date": "2026-08-26",
            "status": "ok"
          },
          {
            "source_website": "trustpilot.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 1,
            "direct_statuses": {
              "403": 1,
              "200": 1
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 12,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2026-09-21",
            "notes": [
              "direct Trustpilot blocked for manheim.com"
            ],
            "errors": [],
            "review_count": 11,
            "existing_review_count": 11,
            "present": true,
            "latest_review_date": "2026-09-21",
            "existing_latest_date": "2026-09-21",
            "status": "ok"
          },
          {
            "source_website": "smartcustomer.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 1
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "missing"
          },
          {
            "source_website": "birdeye.com",
            "attempted": true,
            "direct_pages": 466,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 466
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 35,
            "new_reviews_added": 4,
            "advertised_total": 1439,
            "latest_candidate_date": "2026-10-19",
            "notes": [
              "Birdeye advertised totals may include syndicated Google/Birdeye network reviews; accepted rows are visible textual review cards that pass filters.",
              "Advertised total 1439 is much larger than accepted rows 81; source is likely partially covered after filters/pagination."
            ],
            "errors": [],
            "review_count": 81,
            "existing_review_count": 77,
            "present": true,
            "latest_review_date": "2026-10-12",
            "existing_latest_date": "2026-09-23",
            "status": "partial"
          },
          {
            "source_website": "google.com",
            "attempted": true,
            "direct_pages": 148,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 148
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 5,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2026-07-12",
            "notes": [
              "Google Business Profile discovery completed: 58/58 queries succeeded and 114 unique validated US profiles were selected.",
              "Validated 2 US Google Business Profiles; 9 failed and 103 were skipped after the circuit breaker. Successful profiles were paginated newest-first through per-profile incremental overlap boundaries."
            ],
            "errors": [
              "Maheim Central Florida [0x88e77db086f2d4e5:0xf6e042105c509d3e]: newest review RPC did not load",
              "Manheim [0x88e783036b2fd9ef:0x1e13d3698319c281]: newest review RPC did not load",
              "Manheim [0x88e77d81c99d5285:0x41bfb395696e185]: Response.body: Protocol error (Network.getResponseBody): No data found for resource with given identifier\nResponse body is not available for a response that was navigated away from. Read response.body() before triggering any navigation.",
              "Manheim [0x88f50952666779c7:0x1cc56387cc906fb3]: newest review RPC did not load",
              "Manheim Albany [0x89de141aaae9cfb3:0xeb5b6efd7a533372]: newest review RPC did not load",
              "Manheim Arizona [0x872b0f1ee68b351b:0x321762f77b17cf1c]: newest review RPC did not load",
              "Manheim Atlanta [0x88f502f2aa726a77:0xaa0ac5cbcc382fd5]: newest review RPC did not load",
              "Manheim Atlanta Reconditioning Services [0x88f502f2aa726a77:0xe448884c5d8e6815]: newest review RPC did not load",
              "Manheim auction [0x80dcb1fdaabe2c11:0x6c4d0ec28830eeb6]: newest review RPC did not load"
            ],
            "profile_retention_used": true,
            "profiles_completed": 2,
            "profiles_failed": 9,
            "profiles_skipped_after_circuit_breaker": 103,
            "last_successful_refresh_until": "2026-08-31",
            "review_count": 1480,
            "existing_review_count": 1480,
            "present": true,
            "latest_review_date": "2026-09-30",
            "existing_latest_date": "2026-09-30",
            "status": "partial_profile_retention"
          }
        ]
      },
      {
        "key": "adesa",
        "display_name": "ADESA",
        "until_date": "2026-10-31",
        "since_date": "2023-01-01",
        "review_count": 915,
        "source_counts": {
          "birdeye.com": 111,
          "apps.apple.com": 126,
          "google.com": 601,
          "bbb.org": 11,
          "reddit.com": 26,
          "trustpilot.com": 18,
          "play.google.com": 22
        },
        "source_audit": [
          {
            "source_website": "reddit.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "reddit_pullpush ran; candidate count is not separately tracked for this collector.",
              "reddit_arctic_shift ran; candidate count is not separately tracked for this collector."
            ],
            "errors": [],
            "review_count": 26,
            "existing_review_count": 26,
            "present": true,
            "latest_review_date": "2026-08-14",
            "existing_latest_date": "2026-08-14",
            "status": "ok"
          },
          {
            "source_website": "play.google.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 269,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2026-07-11",
            "notes": [],
            "errors": [],
            "review_count": 22,
            "existing_review_count": 22,
            "present": true,
            "latest_review_date": "2025-06-16",
            "existing_latest_date": "2025-06-16",
            "status": "ok"
          },
          {
            "source_website": "apps.apple.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 206,
            "new_reviews_added": 2,
            "advertised_total": null,
            "latest_candidate_date": "2026-09-30",
            "notes": [
              "Apple RSS can be sparse for some app IDs; HTML supplement captures visible App Store review cards only."
            ],
            "errors": [],
            "review_count": 126,
            "existing_review_count": 124,
            "present": true,
            "latest_review_date": "2026-09-30",
            "existing_latest_date": "2026-09-16",
            "status": "ok"
          },
          {
            "source_website": "bbb.org",
            "attempted": true,
            "direct_pages": 12,
            "fallback_pages": 11,
            "direct_statuses": {
              "403": 12,
              "200": 11
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 4,
            "new_reviews_added": 2,
            "advertised_total": null,
            "latest_candidate_date": "2026-09-15",
            "notes": [
              "direct BBB customer reviews blocked for https://www.bbb.org/us/ca/sacramento/profile/auto-auction/adesa-sacramento-1156-33008688",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/ca/san-diego/profile/auto-auction/adesa-san-diego-1126-23000806",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/fl/tampa/profile/auto-auction/adesa-tampa-0653-24838",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/mn/maple-grove/profile/auto-auction/adesa-minnesota-llc-0704-96174765",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/nv/north-las-vegas/profile/auto-auction/adesa-las-vegas-1086-90040145",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/tn/memphis/profile/auto-auction/adesa-auctions-memphis-0543-44000064",
              "direct BBB complaints blocked for https://www.bbb.org/us/ca/sacramento/profile/auto-auction/adesa-sacramento-1156-33008688",
              "direct BBB complaints blocked for https://www.bbb.org/us/ca/san-diego/profile/auto-auction/adesa-san-diego-1126-23000806",
              "direct BBB complaints blocked for https://www.bbb.org/us/fl/tampa/profile/auto-auction/adesa-tampa-0653-24838",
              "direct BBB complaints blocked for https://www.bbb.org/us/mn/maple-grove/profile/auto-auction/adesa-minnesota-llc-0704-96174765",
              "direct BBB complaints blocked for https://www.bbb.org/us/nv/north-las-vegas/profile/auto-auction/adesa-las-vegas-1086-90040145",
              "direct BBB complaints blocked for https://www.bbb.org/us/tn/memphis/profile/auto-auction/adesa-auctions-memphis-0543-44000064"
            ],
            "errors": [
              "reader error for https://www.bbb.org/us/ca/sacramento/profile/auto-auction/adesa-sacramento-1156-33008688/customer-reviews: HTTPSConnectionPool(host='r.jina.ai', port=443): Read timed out. (read timeout=60)"
            ],
            "review_count": 11,
            "existing_review_count": 9,
            "present": true,
            "latest_review_date": "2026-09-15",
            "existing_latest_date": "2026-09-15",
            "status": "ok"
          },
          {
            "source_website": "trustpilot.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 2,
            "direct_statuses": {
              "403": 1,
              "200": 2
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 11,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2026-08-10",
            "notes": [
              "direct Trustpilot blocked for adesa.com",
              "reader challenge for https://www.trustpilot.com/review/adesa.com?page=2"
            ],
            "errors": [],
            "review_count": 18,
            "existing_review_count": 18,
            "present": true,
            "latest_review_date": "2026-08-10",
            "existing_latest_date": "2026-08-10",
            "status": "ok"
          },
          {
            "source_website": "smartcustomer.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 1
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "missing"
          },
          {
            "source_website": "complaintsboard.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 1
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 1,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2014-02-23",
            "notes": [],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "parsed_no_new_rows"
          },
          {
            "source_website": "birdeye.com",
            "attempted": true,
            "direct_pages": 19,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 19
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 57,
            "new_reviews_added": 8,
            "advertised_total": 663,
            "latest_candidate_date": "2026-10-19",
            "notes": [
              "Birdeye advertised totals may include syndicated Google/Birdeye network reviews; accepted rows are visible textual review cards that pass filters.",
              "Advertised total 663 is much larger than accepted rows 111; source is likely partially covered after filters/pagination."
            ],
            "errors": [],
            "review_count": 111,
            "existing_review_count": 103,
            "present": true,
            "latest_review_date": "2026-10-03",
            "existing_latest_date": "2026-09-23",
            "status": "partial"
          },
          {
            "source_website": "google.com",
            "attempted": true,
            "direct_pages": 126,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 126
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "Google Business Profile discovery completed: 53/53 queries succeeded and 62 unique validated US profiles were selected.",
              "Validated 1 US Google Business Profiles; 6 failed and 55 were skipped after the circuit breaker. Successful profiles were paginated newest-first through per-profile incremental overlap boundaries."
            ],
            "errors": [
              "Adesa [0x89e8459c988e2b7f:0x7a149b2d115bd9b1]: newest review RPC did not load",
              "ADESA Atlanta [0x88f4e6f6bcae32c3:0x8ca5797c8ce4da57]: newest review RPC did not load",
              "ADESA Austin [0x8644c9a7d5710d89:0xc700487a78e37d52]: newest review RPC did not load",
              "Adesa auto auction [0x864ebfe78f765fc1:0xaa6eaa18c8f6c8b7]: newest review RPC did not load",
              "ADESA Birmingham [0x0:0xf16f6e5c92888c0f]: newest review RPC did not load",
              "ADESA Boise [0x54aef62d121ae4d1:0x2b11e609fd0594ed]: newest review RPC did not load"
            ],
            "profile_retention_used": true,
            "profiles_completed": 1,
            "profiles_failed": 6,
            "profiles_skipped_after_circuit_breaker": 55,
            "last_successful_refresh_until": "2026-08-31",
            "review_count": 601,
            "existing_review_count": 601,
            "present": true,
            "latest_review_date": "2026-09-29",
            "existing_latest_date": "2026-09-29",
            "status": "partial_profile_retention"
          }
        ]
      },
      {
        "key": "openlane",
        "display_name": "OPENLANE",
        "until_date": "2026-10-31",
        "since_date": "2023-01-01",
        "review_count": 841,
        "source_counts": {
          "birdeye.com": 20,
          "apps.apple.com": 162,
          "trustpilot.com": 90,
          "play.google.com": 276,
          "google.com": 249,
          "bbb.org": 39,
          "reddit.com": 5
        },
        "source_audit": [
          {
            "source_website": "reddit.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "reddit_pullpush ran; candidate count is not separately tracked for this collector.",
              "reddit_arctic_shift ran; candidate count is not separately tracked for this collector."
            ],
            "errors": [],
            "review_count": 5,
            "existing_review_count": 5,
            "present": true,
            "latest_review_date": "2026-01-18",
            "existing_latest_date": "2026-01-18",
            "status": "ok"
          },
          {
            "source_website": "play.google.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 602,
            "new_reviews_added": 10,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-22",
            "notes": [],
            "errors": [],
            "review_count": 276,
            "existing_review_count": 266,
            "present": true,
            "latest_review_date": "2026-10-21",
            "existing_latest_date": "2026-09-27",
            "status": "ok"
          },
          {
            "source_website": "apps.apple.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 188,
            "new_reviews_added": 9,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-23",
            "notes": [
              "Apple RSS can be sparse for some app IDs; HTML supplement captures visible App Store review cards only."
            ],
            "errors": [],
            "review_count": 162,
            "existing_review_count": 153,
            "present": true,
            "latest_review_date": "2026-10-23",
            "existing_latest_date": "2026-09-15",
            "status": "ok"
          },
          {
            "source_website": "bbb.org",
            "attempted": true,
            "direct_pages": 4,
            "fallback_pages": 4,
            "direct_statuses": {
              "403": 4,
              "200": 4
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 19,
            "new_reviews_added": 6,
            "advertised_total": null,
            "latest_candidate_date": "2026-09-24",
            "notes": [
              "direct BBB customer reviews blocked for https://www.bbb.org/us/in/carmel/profile/car-dealers/openlane-inc-0382-90024496",
              "direct BBB complaints blocked for https://www.bbb.org/us/in/carmel/profile/car-dealers/openlane-inc-0382-90024496",
              "reader challenge for https://www.bbb.org/us/in/carmel/profile/car-dealers/openlane-inc-0382-90024496/complaints?page=2"
            ],
            "errors": [],
            "review_count": 39,
            "existing_review_count": 33,
            "present": true,
            "latest_review_date": "2026-09-24",
            "existing_latest_date": "2026-07-25",
            "status": "ok"
          },
          {
            "source_website": "trustpilot.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 5,
            "direct_statuses": {
              "403": 1,
              "200": 5
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 77,
            "new_reviews_added": 6,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-21",
            "notes": [
              "direct Trustpilot blocked for openlane.com"
            ],
            "errors": [],
            "review_count": 90,
            "existing_review_count": 84,
            "present": true,
            "latest_review_date": "2026-10-21",
            "existing_latest_date": "2026-09-22",
            "status": "ok"
          },
          {
            "source_website": "smartcustomer.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 1
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "missing"
          },
          {
            "source_website": "birdeye.com",
            "attempted": true,
            "direct_pages": 2,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 2
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 10,
            "new_reviews_added": 4,
            "advertised_total": 68,
            "latest_candidate_date": "2026-10-26",
            "notes": [
              "Birdeye advertised totals may include syndicated Google/Birdeye network reviews; accepted rows are visible textual review cards that pass filters.",
              "Advertised total 68 is much larger than accepted rows 20; source is likely partially covered after filters/pagination."
            ],
            "errors": [],
            "review_count": 20,
            "existing_review_count": 16,
            "present": true,
            "latest_review_date": "2026-10-26",
            "existing_latest_date": "2026-09-07",
            "status": "partial"
          },
          {
            "source_website": "google.com",
            "attempted": true,
            "direct_pages": 219,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 219
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "Google Business Profile discovery completed: 106/106 queries succeeded and 2 unique validated US profiles were selected.",
              "Google refresh failed atomically; the last verified Google rows and profile registry were retained."
            ],
            "errors": [
              "OPENLANE [0x87c0f036384b643f:0x7af4135fd6c841d8]: newest review RPC did not load",
              "OPENLANE [0x8814ac6c5df00dff:0x82ddb1a9ae334e23]: newest review RPC did not load",
              "Google Business Profile coverage incomplete: 2/2 profiles failed pagination; first failure: OPENLANE [0x87c0f036384b643f:0x7af4135fd6c841d8]: newest review RPC did not load"
            ],
            "retained_after_failed_refresh": true,
            "last_successful_refresh_until": "2026-08-31",
            "review_count": 249,
            "existing_review_count": 249,
            "present": true,
            "latest_review_date": "2026-09-30",
            "existing_latest_date": "2026-09-30",
            "status": "retained_after_failed_refresh"
          }
        ]
      },
      {
        "key": "acv",
        "display_name": "ACV",
        "until_date": "2026-10-31",
        "since_date": "2023-01-01",
        "review_count": 1204,
        "source_counts": {
          "trustpilot.com": 32,
          "google.com": 963,
          "apps.apple.com": 84,
          "play.google.com": 29,
          "birdeye.com": 84,
          "bbb.org": 11,
          "reddit.com": 1
        },
        "source_audit": [
          {
            "source_website": "reddit.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "reddit_pullpush ran; candidate count is not separately tracked for this collector.",
              "reddit_arctic_shift ran; candidate count is not separately tracked for this collector."
            ],
            "errors": [],
            "review_count": 1,
            "existing_review_count": 1,
            "present": true,
            "latest_review_date": "2023-01-19",
            "existing_latest_date": "2023-01-19",
            "status": "ok"
          },
          {
            "source_website": "play.google.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 125,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2026-08-31",
            "notes": [],
            "errors": [],
            "review_count": 29,
            "existing_review_count": 29,
            "present": true,
            "latest_review_date": "2026-08-21",
            "existing_latest_date": "2026-08-21",
            "status": "ok"
          },
          {
            "source_website": "apps.apple.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 192,
            "new_reviews_added": 2,
            "advertised_total": null,
            "latest_candidate_date": "2026-09-15",
            "notes": [
              "Apple RSS can be sparse for some app IDs; HTML supplement captures visible App Store review cards only."
            ],
            "errors": [],
            "review_count": 84,
            "existing_review_count": 82,
            "present": true,
            "latest_review_date": "2026-09-15",
            "existing_latest_date": "2026-08-26",
            "status": "ok"
          },
          {
            "source_website": "bbb.org",
            "attempted": true,
            "direct_pages": 2,
            "fallback_pages": 2,
            "direct_statuses": {
              "403": 2,
              "200": 2
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 3,
            "new_reviews_added": 1,
            "advertised_total": null,
            "latest_candidate_date": "2026-02-27",
            "notes": [
              "direct BBB customer reviews blocked for https://www.bbb.org/us/ca/san-diego/profile/used-car-dealers/acv-wholesale-1126-20007945",
              "direct BBB complaints blocked for https://www.bbb.org/us/ca/san-diego/profile/used-car-dealers/acv-wholesale-1126-20007945"
            ],
            "errors": [],
            "review_count": 11,
            "existing_review_count": 10,
            "present": true,
            "latest_review_date": "2026-02-27",
            "existing_latest_date": "2026-02-27",
            "status": "ok"
          },
          {
            "source_website": "trustpilot.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 2,
            "direct_statuses": {
              "403": 1,
              "200": 2
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 18,
            "new_reviews_added": 1,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-08",
            "notes": [
              "direct Trustpilot blocked for acvauctions.com",
              "reader challenge for https://www.trustpilot.com/review/acvauctions.com?page=2"
            ],
            "errors": [],
            "review_count": 32,
            "existing_review_count": 31,
            "present": true,
            "latest_review_date": "2026-10-08",
            "existing_latest_date": "2026-09-08",
            "status": "ok"
          },
          {
            "source_website": "smartcustomer.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 1
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "missing"
          },
          {
            "source_website": "birdeye.com",
            "attempted": true,
            "direct_pages": 3,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 3
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 18,
            "new_reviews_added": 9,
            "advertised_total": 4066,
            "latest_candidate_date": "2026-07-05",
            "notes": [
              "Birdeye advertised totals may include syndicated Google/Birdeye network reviews; accepted rows are visible textual review cards that pass filters.",
              "Advertised total 4066 is much larger than accepted rows 84; source is likely partially covered after filters/pagination."
            ],
            "errors": [],
            "review_count": 84,
            "existing_review_count": 75,
            "present": true,
            "latest_review_date": "2026-07-05",
            "existing_latest_date": "2026-07-04",
            "status": "partial"
          },
          {
            "source_website": "google.com",
            "attempted": true,
            "direct_pages": 109,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 109
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "Google Business Profile discovery completed: 53/53 queries succeeded and 1 unique validated US profiles were selected.",
              "Google refresh failed atomically; the last verified Google rows and profile registry were retained."
            ],
            "errors": [
              "ACV Auctions [0x89d3125bc9cd70f3:0xd5d809e01cd8d070]: newest review RPC did not load",
              "Google Business Profile coverage incomplete: 1/1 profiles failed pagination; first failure: ACV Auctions [0x89d3125bc9cd70f3:0xd5d809e01cd8d070]: newest review RPC did not load"
            ],
            "retained_after_failed_refresh": true,
            "last_successful_refresh_until": "2026-09-30",
            "review_count": 963,
            "existing_review_count": 963,
            "present": true,
            "latest_review_date": "2026-09-30",
            "existing_latest_date": "2026-09-30",
            "status": "retained_after_failed_refresh"
          }
        ]
      },
      {
        "key": "americas_auto_auction",
        "display_name": "America's Auto Auction",
        "until_date": "2026-10-31",
        "since_date": "2023-01-01",
        "review_count": 719,
        "source_counts": {
          "birdeye.com": 121,
          "google.com": 594,
          "bbb.org": 4
        },
        "source_audit": [
          {
            "source_website": "reddit.com",
            "attempted": true,
            "direct_pages": 0,
            "fallback_pages": 0,
            "direct_statuses": {},
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "reddit_pullpush ran; candidate count is not separately tracked for this collector.",
              "reddit_arctic_shift ran; candidate count is not separately tracked for this collector."
            ],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "missing"
          },
          {
            "source_website": "bbb.org",
            "attempted": true,
            "direct_pages": 6,
            "fallback_pages": 6,
            "direct_statuses": {
              "403": 6,
              "200": 6
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 2,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2026-01-21",
            "notes": [
              "direct BBB customer reviews blocked for https://www.bbb.org/us/il/centreville/profile/auto-auction/americas-auto-auction-0734-310446804",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/il/crestwood/profile/auto-auction/americas-auto-auction-chicago-0654-12015440",
              "direct BBB customer reviews blocked for https://www.bbb.org/us/tx/buda/profile/auto-auction/americas-auto-auction-austin-0825-90094147",
              "direct BBB complaints blocked for https://www.bbb.org/us/il/centreville/profile/auto-auction/americas-auto-auction-0734-310446804",
              "direct BBB complaints blocked for https://www.bbb.org/us/il/crestwood/profile/auto-auction/americas-auto-auction-chicago-0654-12015440",
              "direct BBB complaints blocked for https://www.bbb.org/us/tx/buda/profile/auto-auction/americas-auto-auction-austin-0825-90094147"
            ],
            "errors": [],
            "review_count": 4,
            "existing_review_count": 4,
            "present": true,
            "latest_review_date": "2026-01-21",
            "existing_latest_date": "2026-01-21",
            "status": "ok"
          },
          {
            "source_website": "trustpilot.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 1,
            "direct_statuses": {
              "403": 1,
              "200": 1
            },
            "blocked": true,
            "fallback_used": true,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [
              "direct Trustpilot blocked for www.americasautoauction.com",
              "reader challenge for https://www.trustpilot.com/review/www.americasautoauction.com"
            ],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "missing"
          },
          {
            "source_website": "smartcustomer.com",
            "attempted": true,
            "direct_pages": 1,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 1
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 0,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": null,
            "notes": [],
            "errors": [],
            "review_count": 0,
            "existing_review_count": 0,
            "present": false,
            "latest_review_date": null,
            "existing_latest_date": null,
            "status": "missing"
          },
          {
            "source_website": "birdeye.com",
            "attempted": true,
            "direct_pages": 22,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 22
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 58,
            "new_reviews_added": 10,
            "advertised_total": 527,
            "latest_candidate_date": "2026-10-31",
            "notes": [
              "Birdeye advertised totals may include syndicated Google/Birdeye network reviews; accepted rows are visible textual review cards that pass filters.",
              "Advertised total 527 is much larger than accepted rows 121; source is likely partially covered after filters/pagination."
            ],
            "errors": [],
            "review_count": 121,
            "existing_review_count": 111,
            "present": true,
            "latest_review_date": "2026-10-31",
            "existing_latest_date": "2026-09-07",
            "status": "partial"
          },
          {
            "source_website": "google.com",
            "attempted": true,
            "direct_pages": 133,
            "fallback_pages": 0,
            "direct_statuses": {
              "200": 133
            },
            "blocked": false,
            "fallback_used": false,
            "candidate_reviews_seen": 6,
            "new_reviews_added": 0,
            "advertised_total": null,
            "latest_candidate_date": "2026-10-05",
            "notes": [
              "Google Business Profile discovery completed: 54/54 queries succeeded and 55 unique validated US profiles were selected.",
              "Validated 2 US Google Business Profiles; 6 failed and 47 were skipped after the circuit breaker. Successful profiles were paginated newest-first through per-profile incremental overlap boundaries."
            ],
            "errors": [
              "America's Auctions In Motion Thousand Oaks [0x80e830983731fbb1:0xf56bc5e71d5f7c65]: newest review RPC did not load",
              "America's Auto Auction Albany [0x88f279eb8fcbfff9:0xbecbdd5ed6e965ae]: newest review RPC did not load",
              "America's Auto Auction Atlanta [0x88f54f77cd6b3ca3:0x6c1da0d0e62c9fa7]: newest review RPC did not load",
              "America's Auto Auction Augusta [0x88f9cb84762e7fc1:0xa5a64f1dc5862f60]: Page.goto: Timeout 60000ms exceeded.\nCall log:\n  - navigating to \"https://www.google.com/maps?cid=11936314851678629728&hl=en&gl=us\", waiting until \"domcontentloaded\"\n",
              "America's Auto Auction Austin [0x865b52ff3d9c30e9:0xebbb605ccf5ba997]: newest review RPC did not load",
              "America's Auto Auction Baton Rouge [0x86269f4057e84d9d:0xb5b13ba60c8bebc1]: newest review RPC did not load"
            ],
            "profile_retention_used": true,
            "profiles_completed": 2,
            "profiles_failed": 6,
            "profiles_skipped_after_circuit_breaker": 47,
            "last_successful_refresh_until": "2026-08-31",
            "review_count": 594,
            "existing_review_count": 594,
            "present": true,
            "latest_review_date": "2026-09-28",
            "existing_latest_date": "2026-09-28",
            "status": "partial_profile_retention"
          }
        ]
      }
    ],
    "stale": []
  }
};
