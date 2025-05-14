# Get u/p credentials from Colab Vault
from google.colab import userdata

nerde_username = userdata.get('nerde_username')
nerde_password = userdata.get('nerde_password')


import requests
import json
import pandas as pd


call = "https://nerde.anl.gov"

# Pull API Token
response = requests.post(
  url=f"{call}/api/auth/login",
  json={
    "userName": nerde_username,  # Remember to replace your username
    "password": nerde_password,  # Remember to replace your password
    "rememberMe": True
  }
)
response


token = response.json()

key = token['result']['token'] # Your unique key
f"{key[:20]}...{key[-20:]}"

# FIPS codes
my_fips = '24011,24013,24015,24017,24019,24021,24023,24025,24027,24029,24031,24033,24035,24039,24037,24041,24043,24045,24047'
# Start and End dates
my_start = '2020-01-01'
my_end = '2023-01-01'


def NERDE_API(section_url, fips, startdate, enddate):
  response = requests.get(
    url=f"{call}{section_url}?county_fips={fips}&start_date={startdate}&end_date={enddate}",
    headers={"Authorization": f"Bearer {key}"}
  ).json()

  results_summary_digest = []

  # Each county will populate a list, this loops through each called county to parse results
  for result in response['result']:
    results_summary_digest.append(result)

  return results_summary_digest


# Create the variable to point to the correct dataset you'd like to pull data from
section_url = "/api/v1/county/explorer/summary"


# API call
summary_digest = NERDE_API(section_url, my_fips, my_start, my_end)


# Create a Pandas DataFrame from summary_digest
main_summary_df = pd.json_normalize(summary_digest)


def update_column_values(df, column_name):
  # Replace 1.0 with 'Yes' and NaN with 'No'
  df[column_name] = df[column_name].apply(lambda x: 'Yes' if x == 1.0 else 'No' if pd.isna(x) else x)

  # Set column to string type
  df[column_name] = df[column_name].astype(str)

  return df


main_summary_df = update_column_values(main_summary_df, 'designated_coal_community')
main_summary_df = update_column_values(main_summary_df, 'nuclear_power_plant_present')


# Create function to un-nest columns
def flatten_column_data(df, list_column, county_column='county', code_column='county_fips'):
  flattened_rows = []

  for _, row in df.iterrows():
    county = row[county_column]
    code = row[code_column]
    for entry in row[list_column]:
      flattened_entry = {
        'County': county,
        'Code': code
      }
      # Add all key-value pairs from the dictionary to the flattened entry
      for key, value in entry.items():
        flattened_entry[key] = value
      flattened_rows.append(flattened_entry)

    return pd.DataFrame(flattened_rows)


# Unemployment Data
unemployment_edci_data = main_summary_df[['county', 'county_fips', 'local_24month_unemployment_rate_series', 'edci_data']]


# Create a new unemployment DataFrame with flattened data
flattened_unemployment_data = flatten_column_data(unemployment_edci_data, 'local_24month_unemployment_rate_series')


# EDCI Indicators Data
edci_data = main_summary_df[['county', 'county_fips', 'edci_indicators']]


# Create a new EDCI DataFrame with flattened data
flattened_edci_data = flatten_column_data(edci_data, 'edci_indicators')


# Demographics API end point
demographics_url="/api/v1/county/explorer/demographics"


# Calling the API
demographics_digest = NERDE_API(demographics_url, my_fips, my_start, my_end)


# Turn response into Dataframe
demographics_df = pd.json_normalize(demographics_digest)


# Annual Demographics Dataframe
demographics_nested_df = demographics[['county', 'county_fips', 'annual_demographics']]


# Annual Demographics Un-nested
demographics_annnual_df = flatten_column_data(demographics_annual, 'annual_demographics')


#Housing API end point
housing_url="/api/v1/county/explorer/housing"


# Calling the API
housing_digest = NERDE_API(housing_url, my_fips, my_start, my_end)


# Turn response into Dataframe
housing_df = pd.json_normalize(housing_digest)


# Workforce API end point
workforce_url = "/api/v1/county/explorer/workforce"


# Calling the API
workforce_digest = NERDE_API(workforce_url, my_fips, my_start, my_end)


# Turn response into Dataframe
workforce_df = pd.json_normalize(workforce_digest)


# Monthly Economic Statistics Dataframe
workforce_monthly_stats = workforce_df[['county', 'county_fips', 'monthly_economic_stats']]


# Monthly Economic Statistics Un-nested
workforce_monthly_stats_flattened = flatten_column_data(workforce_monthly_stats, 'monthly_economic_stats')


# Local Economy URL
localeconomy_url = "/api/v1/county/explorer/localeconomy"


# Calling the API
localeconomy_digest = NERDE_API(localeconomy_url, my_fips, my_start, my_end)


# Turn response into Dataframe
localeconomy_df = pd.json_normalize(localeconomy_digest)


# Industry Employment Dataframe
localeconomy_industry_employment_series = localeconomy_df[['county', 'county_fips', 'state', 'industry_employment_series']]


# Industry Employment Un-nested
localeconomy_industry_employment_series_flattened = flatten_column_data(localeconomy_industry_employment_series, 'industry_employment_series')


# Industry GDP Dataframe
localeconomy_industry_gdp_series = localeconomy_df[['county', 'county_fips', 'state', 'industry_gdp_series']]


# Industry GDP Un-nested
localeconomy_industry_gdp_series_flattened = flatten_column_data(localeconomy_industry_gdp_series, 'industry_gdp_series')


# Industry Trends URL
industrytrends_url="/api/v1/county/explorer/industrytrends"


# Calling the API
industry_digest = NERDE_API(industrytrends_url, my_fips, my_start, my_end)


# Turn response into Dataframe
industry_df = pd.json_normalize(industry_digest)


# Industry Employment Dataframe
industry_location_quotient_series_df = industry_df[['county', 'county_fips', 'location_quotient_series']]


# Industry Employment Un-nested
industry_location_quotient_series_df_flattened = flatten_column_data(industry_location_quotient_series_df, 'location_quotient_series')


# Rist and Resilience URL
risk_url="/api/v1/county/explorer/riskresilience"


# Calling the API
risk_digest = NERDE_API(risk_url, my_fips, my_start, my_end)


# Turn response into Dataframe
risk_df = pd.json_normalize(risk_digest)


# Rename Column
risk_df.rename(columns={"geo_fips": "county_fips"}, inplace=True)


# Risk FEMA Disaster Declarations Dataframe
risk_fema_disaster_dec_df = risk_df[['county', 'county_fips', 'fema_disaster_declarations']]


# Risk FEMA Disaster Declarations Un-nested
risk_fema_disaster_dec_df_flatten = flatten_column_data(risk_fema_disaster_dec_df, 'fema_disaster_declarations')



