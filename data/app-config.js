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
  }
};
