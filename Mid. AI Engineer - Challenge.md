**AI Engineer**  
**Challenge**  
PT Synapsis Sinergi Digital

1. ## **Scenario**

## A coal mining company aims to optimize its mining operations using production data. Your task is to design and implement a data pipeline that collects, transforms, and loads coal production data from various sources into a data warehouse. Additionally, you will validate the data and create a dashboard to visualize key production metrics.

2. ## **Data Sources**

## Please you can download the datasets file [here](https://drive.google.com/file/d/1rdX3i-YfZaqul1KIR8Tw6QiR1MJsdif-/view?usp=sharing), that includes :

1. **SQL Database:** A table production\_logs with columns date, mine\_id, shift, tons\_extracted, quality\_grade.  
2. **IoT Sensors:** A CSV file equipment\_sensors.csv with columns timestamp, equipment\_id, status, fuel\_consumption, maintenance\_alert.  
3. **API:** Provides daily weather data for Berau, Kalimantan, Indonesia (latitude: 2.0167° N, longitude: 117.3000° E) via the Open-Meteo API endpoint https://api.open-meteo.com/v1/forecast?latitude=2.0167\&longitude=117.3000\&daily=temperature\_2m\_mean,precipitation\_sum\&timezone=Asia/Jakarta\&past\_days=0\&start\_date=**{date}**\&end\_date=**{date}** the date is formatted with YYYY-MM-DD and returning {"latitude":2,"longitude":117.25,"generationtime\_ms":4.30583953857422,"utc\_offset\_seconds":25200,"timezone":"Asia/Jakarta","timezone\_abbreviation":"GMT+7","elevation":44,"daily\_units":{"time":"iso8601","temperature\_2m\_mean":"°C","precipitation\_sum":"mm"},"daily":{"time":\["2025-06-01"\],"temperature\_2m\_mean":\[26.2\],"precipitation\_sum":\[3.4\]}}

   

3. ## **Challenge Task**

1. ### **Design the Data Pipeline**

### You can use analytical databases like clickhouse or apache doris to do this challenge. Make sure that everything is run on docker so we can replicate it. 

1. ### **Extraction:**

* ### Retrieve daily production data from the production\_logs table using an SQL query.

* ### Read the equipment\_sensors.csv file for mining equipment sensor data.

* ### Call the weather API to fetch daily weather data.

2. ### **Transformation :** Generate the following metrics :

* ### total\_production\_daily: Total tons of coal mined per day.

* ### average\_quality\_grade: Average coal quality per day

* ### equipment\_utilization: Percentage of time equipment is operational (status "active") per day.

* ### fuel\_efficiency: Average fuel consumption per ton of coal mined.

* ### weather\_impact: Correlation between rainfall and daily production (e.g., production on rainy vs. non-rainy days).

3. ### **Handling Missing or Invalid Data:**

* ### If tons\_extracted is negative, replace it with 0 or flag it as an anomaly.

* ### If sensor data is missing for an equipment, use the previous day’s average or mark as "unknown".

2. ### **Implement the ETL Script**

1. ### Write a Python script to extract, transform, and load the data into a data warehouse table named daily\_production\_metrics.

2. ### Use SQL queries for database operations where necessary.

3. ### **Validate the Data**

1. ### Implement checks:

   * Ensure total\_production\_daily is not negative.

   * Verify equipment\_utilization is between 0 and 100%.

   * Confirm weather data is complete for each production day.

2. Handle anomalies: Log errors to a separate file or send notifications for further analysis.

4. ### **Create a Dashboard**

1. ### Use Metabase (or a tool like Power BI/Superset) to create a dashboard with at least three visualizations:

   * **Line Chart:** Daily production trends (total\_production\_daily) over one month.

   * **Bar Chart:** Comparison of average\_quality\_grade across mines (mine\_id).

   * **Scatter Plot:** Relationship between rainfall (rainfall\_mm) and daily production (total\_production\_daily).

5. ### **Document and Version Control**

1. ### Write a brief report (1-2 pages) explaining the pipeline design, ETL process, and validation steps.

2. ### Use Git for versioning the code and provide a link to the repository.

6. ### **Bonus Point**

### Use collected data to make a production data prediction model. Do a time series forecasting model to predict next day production data. Only do this bonus part if you have done all the challenges.

4. ## **Rules**

1. The challenge must be submitted in  **4 days** after you get this challenge.   
2. If you can complete the challenge test before the deadline, it will be taken into consideration by us.

5. ## **Expected Deliverables**

All deliverables **must be included in the GitHub repository**, including documents, images, and Python code.  Make sure to invite **mufidmove@gmail.com** a collaborator & reviewer on the github repository.

 The following deliverables must be submitted :

1. Data pipeline design document (in PDF format).  
2. Python script and SQL queries (if applicable).  
3. Dockerfile and docker config file (if any).  
4. Dashboard (screenshot or link).  
5. Documentation report.

   **– Do Your Best \-**