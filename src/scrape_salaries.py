import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def scrape_hoopshype_salaries():
    url = "https://hoopshype.com/salaries/players/"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    players = []
    salaries = []

    rows = soup.find_all("tr")
    for row in rows:
        name_cell = row.find("td", class_="name")
        if name_cell:
            name = name_cell.get_text(strip=True)
            salary_cell = name_cell.find_next_sibling("td")
            if salary_cell and salary_cell.has_attr("data-value"):
                salary_value = salary_cell["data-value"]
                salary = int(salary_value)
                players.append(name)
                salaries.append(salary)
    
    # Create DataFrame
    df = pd.DataFrame({
        "PLAYER_NAME": players,
        "SALARY": salaries
    })

    return df

if __name__ == "__main__":
    df = scrape_hoopshype_salaries()

    # Save to CSV
    df.to_csv("data/player_salaries.csv", index=False)

    print(f"Saved {len(df)} records to data/player_salaries.csv")
