# **Compliance Metrics**
Ever wonder how [locked in](https://www.urbandictionary.com/define.php?term=Locked+In) you actually are? There's famous quote that says: "What gets measured gets done". In an effort to keep myself accountable regarding my schedule, I started using Google Sheets to track all kinds of things on a daily basis. The simple act of logging things has proved to help me comply to my regimen, but by doing some (extremely basic) statistical analysis I have been able to identify patterns that lead to higher compliance rates. By creating a yaml file outlining what you want to track, this script will create a Google Sheet which you can use to log your activities. After the selected period of time has passed, the `report` command will pull down the data from the Google Sheet, parse the data using pandas, create a couple of visualizations using plotly, and generate a written report (pdf) giving you some insights about your compliance.

# **Set Up**
1. Clone this repository
2. Enable the GoogleSheets and GoogleDrive apis in the Google Cloud Console
3. Download your credentials from Google and paste them in a file called `credentials.json` in the same directory as the `Justfile`
4. Create a `.env` file with an env variable as follows `GMAIL=youremail@gmail.com`
5. Run `just setup-dev` to install the dependencies
6. You are now ready

# **metrics.yaml**
The exact schema definitions are in a filed called `models.py` if you'd like to look at that. The general schema for the `metrics.yaml` file is as follows:
```
    sheet_name: What you want to call the Google Sheet
    start_tracking_date: The first day of logging
    end_tracking_date: The last day of logging
    metrics: The list of metrics you want to log
```
Each of the metrics you want to log should look like this:
```
    name: The name of the task
    data_type: What data type ("int", "float", "enum")
    values: If data_type == "enum", define the enum values here (Ex: Yes, No)
    goal: Goal
```
The goal field is important because we use these values to define a "success". The goal field should have this schema:
```
    target_value: What we were aiming for, weight under 180 lbs, or "yes" for gym attendance
    operator: Do we want our value to be >, >=, <, <= (this is exclusive for int/float values)
```
When we calculate the compliance rates we compare every day's entry to the Goal you defined in the `metrics.yaml` file.

# **Commands**
### setup
After you modify the `metrics.yaml` to include everything you want to track, run `just compliance-metrics setup`. This command will create a Google Sheet that with a column for every one of the tasks you want to track. You should receive an email granting you access to the newly created spreadsheet soon after running the command. Please don't alter the column names or general structure of the sheet as it will likely break the `report` logic.

### report
Once the defined period of time has passed, run `just compliance-metrics report`. This command will pull down all the data from the Google Sheet and generate the pdf. The report be created in the `reports` directory.
