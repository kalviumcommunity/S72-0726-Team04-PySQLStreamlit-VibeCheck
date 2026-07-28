## 📅 30‑Day Roadmap with Detailed Tasks
# Week 1 (28 Jul – 3 Aug): Data Intake & Preparation
# Day 1 (28 Jul)

Gaurav: Set up Python workspace, GitHub repo, and folder structure for the project.

Vedant: Collect raw datasets (onboarding progress, tool usage logs, support tickets). Document sources and formats.

Aayush: Draft initial PRD (problem → product requirements). Define what “friction points” mean in measurable terms.

# Day 2 (29 Jul)

Gaurav: Write ingestion scripts for CSV/JSON files (onboarding dataset).

Vedant: Validate schema, encoding, and formats for tool usage logs.

Aayush: Profile support request dataset (nulls, duplicates, ranges).

# Day 3 (30 Jul)

Gaurav: Build reusable functions for reading and cleaning onboarding data.

Vedant: Handle missing values in tool usage logs (e.g., impute login counts).

Aayush: Detect duplicates in support requests and decide retention rules.

# Day 4 (31 Jul)

Gaurav: Standardize data types (dates, booleans, categories) in onboarding dataset.

Vedant: Normalize string fields (tool names, actions).

Aayush: Transform timestamps in support requests into day/hour/week features.

# Day 5 (1 Aug)

Gaurav: Create data dictionary mapping onboarding fields to business meaning.

Vedant: Document tool usage metrics (frequency, active days).

Aayush: Map support request categories to business context.

# Day 6 (2 Aug)

Gaurav: Detect outliers in onboarding completion times.

Vedant: Apply consistency rules to tool usage logs (e.g., login count ≥ 0).

Aayush: Flag anomalies in support request volume.

# Day 7 (3 Aug)

Team sync: Review cleaned datasets, align schemas, and plan merge strategy.

---

## Week 2 (4 – 10 Aug): Integration & Feature Engineering

# Day 8 (4 Aug)

Gaurav: Merge onboarding + tool usage datasets. Validate joins.

Vedant: Merge support requests with merged dataset. Handle unmatched keys.

Aayush: Document merged schema and business meaning.

# Day 9 (5 Aug)

Gaurav: Engineer features (e.g., “days to complete onboarding”).

Vedant: Create tool usage ratios (active days / total days).

Aayush: Create support request features (avg resolution time).

# Day 10 (6 Aug)

Gaurav: Distribution analysis of onboarding completion times.

Vedant: Correlation analysis between tool usage and onboarding speed.

Aayush: Segment support requests by type and frequency.

# Day 11 (7 Aug)

Gaurav: Behavioural analysis of new hires (fast vs slow onboarding).

Vedant: Funnel analysis of tool adoption stages.

Aayush: KPI definition (e.g., “% hires completing onboarding in 30 days”).

# Day 12 (8 Aug)

Gaurav: Root cause investigation for delayed onboarding.

Vedant: Anomaly detection in tool usage patterns.

Aayush: SQL integration — load cleaned data into database.

# Day 13 (9 Aug)

Gaurav: Write SQL queries for onboarding KPIs.

Vedant: SQL queries for tool usage metrics.

Aayush: SQL queries for support request metrics.

# Day 14 (10 Aug)

Team sync: Build first integrated dataset + SQL layer for analysis.

---

## Week 3 (11 – 17 Aug): Insights & Dashboard

# Day 15 (11 Aug)

Gaurav: SQL window functions for ranking hires by onboarding speed.

Vedant: Optimise SQL queries for tool usage.

Aayush: Create SQL views for reporting.

# Day 16 (12 Aug)

Gaurav: Validate SQL vs Python outputs.

Vedant: Design visualisation principles (charts for onboarding vs tool usage).

Aayush: Build interactive Plotly charts for support requests.

# Day 17 (13 Aug)

Gaurav: Design KPI cards (onboarding completion rate).

Vedant: Write insight narrative (tool adoption bottlenecks).

Aayush: Draft executive summary (support request impact).

# Day 18 (14 Aug)

Gaurav: Export cleaned datasets + charts.

Vedant: Build Streamlit app structure.

Aayush: Implement dataset upload + preview in Streamlit.

# Day 19 (15 Aug)

Gaurav: Add filters for onboarding cohorts.

Vedant: Add session state persistence.

Aayush: Build real‑time KPI dashboard.

# Day 20 (16 Aug)

Gaurav: Add alert monitoring (delayed onboarding).

Vedant: Integrate email report sharing.

Aayush: Automate pipeline execution.

# Day 21 (17 Aug)

Team sync: Demo Streamlit prototype showing friction insights.

---

## Week 4 (18 – 24 Aug): Automation & Delivery

# Day 22 (18 Aug)

Gaurav: Set up GitHub Actions for pipeline validation.

Vedant: Document dashboard usage.

Aayush: Refine PRD with final scope.

# Day 23 (19 Aug)

Gaurav: Mock UX design for dashboard improvements.

Vedant: Polish KPI cards and charts.

Aayush: Draft stakeholder communication plan.

# Day 24 (20 Aug)

Gaurav: Integrate alerts into dashboard.

Vedant: Validate SQL vs Python outputs again.

Aayush: Prepare executive report.

# Day 25 (21 Aug)

Gaurav: Test automated pipeline end‑to‑end.

Vedant: Review documentation.

Aayush: Format final report.

# Day 26 (22 Aug)

Gaurav: Finalise GitHub workflows.

Vedant: Dashboard polish.

Aayush: Report polish.

# Day 27 (23 Aug)

Team sync: Dry run of full product workflow.

# Day 28 (24 Aug)

Gaurav: Bug fixes.

Vedant: Dashboard refinements.

Aayush: Report refinements.

## Final Days (25 – 26 Aug): Delivery
# Day 29 (25 Aug)

Team: Prepare final presentation deck + demo.

# Day 30 (26 Aug)

Team: Deliver unified data product to leadership, showing onboarding friction points.

---

Gaurav → Data ingestion, cleaning, pipeline automation, GitHub workflows.

Vedant → Tool usage dataset handling, SQL optimisation, dashboard building.

Aayush → Support request analysis, reporting, stakeholder communication.