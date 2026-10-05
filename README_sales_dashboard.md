# Sales Performance Dashboard

Clean a raw sales dataset, analyze trends, and present the results in an interactive dashboard.

## Files

| File | Purpose |
|------|---------|
| `raw_sales.csv` | Raw data (6,150 rows) with deliberate nulls and duplicates |
| `cleaned_sales.csv` | Cleaned data (5,417 rows). **Import this into Power BI or Tableau** |
| `sales_analysis.py` | Python pipeline: generate, clean, analyze, build dashboard |
| `sales_dashboard.html` | Interactive dashboard (open in any browser) |

The dataset is a sample generated for this project (3 years, 4 regions, 5 categories, 20 products, amounts in INR). To use your own data, point `RAW_CSV` in the script at your file. It needs these columns: `order_id, order_date, region, category, product, quantity, unit_price, discount, revenue, profit`.

## Steps Completed

1. **Import and clean.** 150 exact duplicate rows removed, then 583 rows containing nulls removed (613 null cells in total, some rows had several). Dates converted to a date type, quantity to integer, and year, month, and quarter columns added.
2. **Trends.** Monthly, quarterly, and yearly revenue and profit (toggle on the dashboard).
3. **Products.** Top 5 and bottom 5 by revenue.
4. **Comparisons.** Region-wise and category-wise revenue and profit.
5. **KPIs.** Total revenue, total profit, profit margin, and year-over-year growth rate.
6. **Dashboard.** Filters for year, region, and category update every KPI and chart.

## Key Findings (sample data)

| Metric | Result |
|--------|--------|
| Total revenue | 6.53 Cr |
| Total profit | 1.79 Cr (27.4% margin) |
| Revenue growth | +10.0% in 2023, +9.4% in 2024 |
| Best region | North (1.97 Cr); weakest is East (1.25 Cr) |
| Best category | Electronics (3.58 Cr, 55% of revenue) |
| Top products | Laptop, Smartphone, Headphones |
| Seasonality | Q4 is the strongest quarter every year |

**Reading "low-performing" carefully:** the bottom 5 by revenue (Water Bottle, Bookshelf, Notebook Pack, File Organizer, Pen Set) are mostly cheap, high-volume items. Low revenue does not mean low profit. Water Bottle sold about 1,980 units at a healthy margin.

## Building the Same Dashboard in Power BI

1. **Get Data > Text/CSV** and load `cleaned_sales.csv`. In Power Query, confirm `order_date` is *Date* and the amounts are *Decimal*.
2. Optionally create a Date table: `Calendar = CALENDAR(MIN(cleaned_sales[order_date]), MAX(cleaned_sales[order_date]))`, and relate it to `order_date`.
3. Add these measures:
   ```
   Total Revenue = SUM(cleaned_sales[revenue])
   Total Profit  = SUM(cleaned_sales[profit])
   Profit Margin = DIVIDE([Total Profit], [Total Revenue])
   Revenue PY    = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Calendar'[Date]))
   Growth Rate   = DIVIDE([Total Revenue] - [Revenue PY], [Revenue PY])
   ```
4. **KPIs:** four *Card* visuals for Total Revenue, Total Profit, Profit Margin, and Growth Rate.
5. **Trend:** a *Line chart* with the Date hierarchy on the axis. Use the drill-down arrows for year, quarter, and month.
6. **Products:** a *Bar chart* of `product` by Total Revenue. Add a Top N filter (Top 5, then Bottom 5).
7. **Comparison:** a *Clustered column chart* of `region` and another of `category`, each showing Revenue and Profit.
8. **Interactivity:** add *Slicers* for year, region, and category. Cross-filtering between visuals works automatically.

## Building the Same Dashboard in Tableau

1. **Connect > Text file** and choose `cleaned_sales.csv`.
2. Create a calculated field `Profit Margin = SUM([profit]) / SUM([revenue])`.
3. **Trend:** drag `order_date` to Columns (right-click for Year, Quarter, or Month) and `revenue` to Rows.
4. **Products:** drag `product` to Rows and `revenue` to Columns, sort descending, and add a Top N filter.
5. **Comparison:** build one bar chart by `region` and one by `category`, each with revenue and profit.
6. **Growth:** right-click the revenue measure > *Quick Table Calculation* > *Year over Year Growth*.
7. **Dashboard:** combine the sheets, then use *Show Filter* for year, region, and category. Set the filters to *Apply to Worksheets > All Using This Data Source*.

## Note

I could not produce a `.pbix` or `.twbx` file directly, since those tools need their own desktop applications. The HTML dashboard has the same KPIs, charts, and filters, and the steps above rebuild it in either tool from the cleaned CSV.
