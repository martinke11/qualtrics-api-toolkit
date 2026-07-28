# qualtrics-api-toolkit
Repository for managing all scripts associated with using the Qualtrics API and generating reports from it.

## Configuration

`qualtrics_api_toolkit` can be installed as a Python package using either Anaconda or a standard Python virtual environment.

Installing the package allows it to be imported from any script running in that environment without adding the repository path to `config.json` or changing the working directory.


### Install with Windows Command Prompt

Open Command Prompt and navigate to the cloned repository:

```bat
cd C:\path\to\qualtrics-api-toolkit
```

Create a virtual environment using the desired Python installation:

```bat
C:\path\to\python.exe -m venv .venv
```

For example:

```bat
C:\Users\YourUsername\AppData\Local\Programs\Python\Python313\python.exe -m venv .venv
```

Activate the virtual environment:

```bat
.venv\Scripts\activate.bat
```

The command prompt should now display `(.venv)` before the current directory:

```text
(.venv) C:\path\to\qualtrics-api-toolkit>
```

Upgrade pip:

```bat
python -m pip install --upgrade pip
```

Install the package in editable mode:

```bat
python -m pip install -e .
```

After installation, the package can be imported with:

```python
import qualtrics_api_toolkit.qual_api as qa

from qualtrics_api_toolkit.utils import (
    QUALTRICS_CREDS,
    get_token,
)
```

### Install with Anaconda

Open Anaconda Prompt and navigate to the cloned repository:

```bat
cd C:\path\to\qualtrics-api-toolkit
```

Activate the Conda environment in which the package should be installed:

```bat
conda activate your_environment
```

Install the package in editable mode:

```bat
python -m pip install -e .
```

To install the package without changing any existing dependencies in the Conda environment, use:

```bat
python -m pip install --no-deps -e .
```

### Configure API Credentials

All users must create a `config.json` file that identifies the location of their Qualtrics API credentials file.

If the package is installed, only `qualtrics_credentials_path` is required:

```json
{
  "qualtrics_api": {
    "qualtrics_credentials_path": "C:\\path\\to\\qualtrics_credentials.txt"
  }
}
```

The `qualtrics_credentials_path` value must contain the full path to the file containing the user’s Qualtrics API credentials.

### Use the Repository Without Installing the Package

Installing `qualtrics_api_toolkit` is the recommended approach. However, users may instead clone the repository and configure Python to load the package directly from the local source code.

When using the repository without installing it, add the optional `qualtrics_api_root` value to `config.json`:

```json
{
  "qualtrics_api": {
    "qualtrics_api_root": "C:\\path\\to\\qualtrics-api-toolkit",
    "qualtrics_credentials_path": "C:\\path\\to\\qualtrics_credentials.txt"
  }
}
```

The configuration values are:

* `qualtrics_credentials_path`: Required for all users. The full path to the file containing the Qualtrics API credentials.
* `qualtrics_api_root`: Required only when using the cloned repository without installing the package. The root directory of the local `qualtrics-api-toolkit` repository.


When using this method, the project’s `src` directory must be added to Python’s import path before importing the toolkit.

After cloning the repository and creating a `config.json` file containing your local paths, update the following files:

1. ```text
   qualtrics-api-toolkit\src\qualtrics_api_toolkit\utils\config.py
   ```

   Comment out the package-installation configuration at the top of the file and use the alternative configuration code provided in the commented section at the bottom.

2. ```text
   qualtrics-api-toolkit\src\qualtrics_api_toolkit\utils\__init__.py
   ```

   Uncomment both references to: PROJECT_DIRECTORY

These changes configure the toolkit to locate the repository and credentials file using the paths defined in `config.json`, rather than relying on an installed package.


Installing the package is the recommended approach because it avoids modifying `sys.path` or changing the working directory at runtime.

### Credentials

Do not commit Qualtrics credentials to GitHub. Store the credentials file outside the repository or add it to `.gitignore`.
In a plain text file named copa_qualtrics_credentials.txt API Credentials(ClientID, Client Secret, and Data Center)

## Navigation
qual_api contains python modules that are organized by task type.

that stores all functions that need to be used for various tasks accross various scripts. This includes generating the token, pulling the list of surveys, and creating data frames required to analyze the survey responses. The final data frame is responses_df and will be used accross the script for anaylsis, where each script will make further transformations to responses_df depending on the task. There are additional functions that can be used for account management tasks to such as managing users, groups, mailing and contact lists, etc. Functions that only need to be run within 1 script(for a specific task after responses_df is loaded and cleaned) should be kept within that script. For example, the function translate_seperate_text_df in [translation.py](https://github.com/martinke11/Qualtrics_API_Program/blob/main/translation.py) is used for translation only and should be kept in the script doing the translation.

import statement: <br /> import QualAPI as qa
<br /> 

### Frequency & Count Report: [frequency_count_report.py](https://github.com/martinke11/Qualtrics_API_Program/blob/main/frequency_count_report.py)
This script generates a report in word doc that includes:
1) A table for every quantitative question with the Question answer value, the assinged question answer values code (i.e. yes = 1, no = 2, for visualization purposes in case answer options are too long and dont present well in the chart), the count, and the frequency of the answers. 
2) Corresponding bar chart visualizations for the frequency distrobutions. Currently displays % on bars but can be updated to present count or even % and count together by updateing lines 247 - 259.
3) Page break between each question.

You will need to add a folder titled 'Reports' to the repo locally on your computer and then add it to .gitignore. This folder is where the output from the word doc is placed. It can also be used for any other output documentation from any of the other scripts.

NULL Included in analysis and visualizations: Because, in many cases, respondents skip certain questions, NULL responses are kept for each question to prevent confusion around inconsistant total responses across questions in a survey. Including NULL can also provide insight to which questions could be reworked/edited to be clearer/easier for the respondant (if NULL is particuarily high for a given question.) NULL responses are visualized with a red bar instead of blue. 

Current Version makes tables and plots of Multiple Choice Questions: Single Choice, Multiple Choice, Dropdown Lists, Random Choice, Matrix, and Numeric Questions: Rank Order, Sliders
- Not set up to do Side by Side questions(SBS/SBSMatrix), which should be avoided.
- Text Questions are not plotted here
- For Slider questions that use the Star visuals, surveys should be made with the default 5 stars, currently there is no way to automatically identify how many Stars were set in the survey. If a survey has a different about of stars, line 766 (slider_range = range(1, 6)) in the handle_slider_question function in [QualAPI.py](https://github.com/martinke11/Qualtrics_API_Program/blob/main/QualAPI.py) will need to be updated manually.

### Pre & Post Survey Frequency Count Report: [pre_post_matching_and_analysis_with_same_survey.py](https://github.com/martinke11/Qualtrics_API_Program/blob/main/pre_post_matching_and_analysis_with_same_survey.py)<br>
This script does the same analysis as [frequency_count_report.py](https://github.com/martinke11/Qualtrics_API_Program/blob/main/frequency_count_report.py) but for pre and post data that was collected in the same survey with no unique ids. So the script first uses fuzzy matching to match pre and post responses, assigns a unique ID to each match, and then generates a report via word document.

### Pre & Post General Analysis: [pre_post_general_analysis.py](https://github.com/martinke11/Qualtrics_API_Program/blob/main/pre_post_general_analysis.py)
This script houses buildible code for pre and post analysis where pre and post data was collected in two seperate surveys, or the same survey with pre and post data defined by a cutt-off date, or the same survey with fuzzy matching on names or other attributes to determine pre and post responses.

### Translation Script: [translation.py](https://github.com/martinke11/Qualtrics_API_Program/blob/main/translation.py)
[Google Translate library documentation](https://libraries.io/pypi/googletrans/4.0.0rc1)
- googletrans 4.0.0rc1 is the best *free* api tool for translating data
  
There are 2 methods for transcribing a data frame:
1) translate_seperate_text_df function keeps the original untranslated column(s) and adds the new/translated column(s) next to it. Can be used for comparison purposes or checking with a native speaker.
2) translate_replace_full_df function replaces the original untranslatted column(s) with the translated column(s).

Currently this script end with optional code to export the translated version as a csv file. However, this script can be used as a py-module to import the translated data frame into nlp_analysis.py script for further NLP analysis.

### Free Text Compliance Script: [free_text_compliance.py](https://github.com/martinke11/Qualtrics_API_Program/blob/main/free_text_compliance.py)
Gets a count + percentage of how many respondents completed each free text question. Useful for when deciding to do any NLP analysis by understanding the sample size i.e. if only 10 or 20 (or whatever number depending on the project) responses completed a free text question its likely not worth pursuing NLP analysis. 

### [Account Management Folder](https://github.com/martinke11/Qualtrics_API_Program/tree/main/Account_Management)
This folder holds scripts that can be used to build out other workflows in questions such as group, user, contact, and mailing list management.

