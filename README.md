# AgriExport Market Analysis System

> A MongoDB-powered export analytics dashboard for agricultural products with profitability, market intelligence, and seasonal planning insights.

---

## Features

- Analyze agricultural export products, markets, and logistics in one integrated system
- Identify the most profitable country for each export product
- Calculate competitive selling prices using production cost, shipping, and tariffs
- Generate profitability matrix for product-country combinations
- Detect high-profit and low-margin export opportunities
- Plan seasonal exports using harvest cycles, market demand, and transit time
- Interactive Streamlit dashboard with KPI cards, charts, filters, and tables
- Cloud-ready deployment using MongoDB Atlas and Streamlit Cloud

---

## Tech Stack

- Python
- MongoDB
- PyMongo
- Streamlit
- Plotly
- Pandas
- MongoDB Atlas

---

## Installation

```bash
git clone <repo-link>
cd AgriExport
pip install -r requirements.txt
streamlit run app.py

## Environment Variables

Create a .streamlit/secrets.toml file and add:

MONGO_URI = "your_mongodb_atlas_connection_string"
Usage

Open the Streamlit app in your browser:

http://localhost:8501

Use the dashboard to:

Explore product data
Analyze country-wise market trends
Compare profitability across export markets
View seasonal export recommendations
Project Structure
AgriExport/
│
├── app.py
├── db.py
├── requirements.txt
├── README.md
│
├── pages/
│   ├── Products.py
│   ├── Market_Analysis.py
│   ├── Profitability.py
│   └── Seasonal_Planning.py
│
└── .streamlit/
    └── secrets.toml
Modules
Products

View product details including category, origin, shelf life, harvest season, and cost structure.

Market Analysis

Analyze export destinations using tariff rates, exchange rates, demand levels, and quality preferences.

Profitability

Evaluate profit margins across all product-country combinations using cost, tariff, and logistics data.

Seasonal Planning

Plan export schedules based on harvest windows, demand patterns, and transit suitability.

Author

Achal
