**Sesame Workshop Take Home Project**

Welcome to this project! I was tasked to model a series of tables to add ease to future analysts' work. I did not model every column in every table in the the folders, but rather selectively chose the columns relevant to the prompts.

Before I "started the clock," I reviewed the files and explored the data a bit to familiarize myself to the schema. I reviewed DuckDB documentation and identified how to best utilize the package for this project. 

With the clock started, I began working through the brief, first creating tables to answer the verification questions, then to answer the memos. I aimed to make the fact tables easy to follow and useable for future analysts to answer the brief's questions. Additionally, I aimed to clean up the fact tables enough that the analysts would not have to spend time formatting columns before using the tables.


*The Model*

I chose to create three fact tables to reflect the themes I saw in the brief: fct_ga_events, fct_donations, and fct_ratings. These fact tables are build from various raw tables which were cleaned up and transformed into staging tables, then joined into the fact tables. 

*Navigation*

Please start by reviewing the BRIEF.pdf as this was my guiding force for this project. 

Next, the run_pipeline.py contains the modeled tables and answers to the prompted questions. (More on the python environment setup in a bit.) 

Along side the run_pipeline.py, I recommend examining the DECISION_MEMO.md to understand my thought process and more extensive answers to the prompts. 


*Setup*

Please view pyproject.toml to make sure the right packages/versions are installed for the project.

DuckDB was a key component in running this project. I enjoyed reading through the documentation on the page, and I found it to be quite helpful, especially for properly uploading the files in the format desired. 

Review DuckDB here: https://duckdb.org/install/?platform=windows&environment=python
