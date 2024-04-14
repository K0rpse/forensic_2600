browser_artifacts = {
      "firefox": {
          "profile": [r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\",
                      r"Users\\[^\\]+\\AppData\\Local\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\"],
          "bookmarks/history": [
              r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\places.sqlite"],
          "bookmarks_backup": r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\bookmarkbackups",
          "cookies": r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\cookies.sqlite",
          "cache": [r"Users\\[^\\]+\\AppData\\Local\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\cache2\\entries",
                    r"Users\\[^\\]+\\AppData\\Local\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\startupCache"],
          "form_history": [
              r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\formhistory\.sqlite"],
          "addons/extensions": [
              r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\addons\.sqlite",
              r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\extensions\.sqlite"],
          "favicons": [
              r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\favicons\.sqlite"],
          "settings": [r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\prefs\.js"],
          "logins/passwords": [
              r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\logins\.json",
              r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\key[0-9]\.db"],
          "session_data": [
              r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\sessionstore\.jsonlz4",
              r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\sessionstore-backups"],
          "downloads": [
              r"Users\\[^\\]+\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\downloads\.sqlite"],
          "thumbnails": [r"Users\\[^\\]+\\AppData\\Local\\Mozilla\\Firefox\\Profiles\\[^\\]+\.default\\thumbnails"]

      },
      "chrome": {'profile': [r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\Default$",
                             r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\ChromeDefaultData$"],
                 'history/downloads': [r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History$",
                                       r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\ChromeDefaultData\\History$"],
                 'cookies': [r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\ChromeDefaultData\\Cookies$",
                             r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies$"],
                 'cache': [r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache$",
                           r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\ChromeDefaultData\\Cache$"],
                 'bookmarks': [
                     r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\ChromeDefaultData\\Bookmarks$",
                     r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks$"],
                 'forms_history': [
                     r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\Web Data$"],
                 'favicons': [
                     r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\Favicons$"],
                 'logins': [
                     r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\Login Data$"],
                 'current_sessions/tabs': [
                     r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\(?:Current Session|Current Tabs|Current Tabs-Last)$"],
                 'previous_sessions/tab': [
                     r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\(?:Last Session|Last Tabs|Last Tabs-Last)$"],
                 'extensions': [
                     r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\Extensions\\$"],
                 'thumbnails': [
                     r"Users\\[^\\]+\\AppData\\Local\\Google\\Chrome\\User Data\\(?:ChromeDefaultData|Default)\\(?:Top Sites|Thumbnails)$"]
                 },
      "edge": {
          "profile_path": [r"Users\\[^\\]+\\AppData\\Local\\Packages\\Microsoft\.MicrosoftEdge_[0-9A-z]{0,60}\\AC$"],
          "history/cookies/downloads": [
              r"Users\\[^\\]+\\AppData\\Local\\Microsoft\\Windows\\WebCache\\WebCacheV01\.dat$"],
          "settings": [
              r"Users\\[^\\]+\\AppData\\Local\\Packages\\Microsoft\.MicrosoftEdge_[0-9A-z]{0,60}\\AC\\MicrosoftEdge\\User\\Default\\DataStore\\Data\\[^\\]+\\[^\\]+\\DBStore\\spartan\.edb$"],
          "cache": r"Users\\[^\\]+\\AppData\\Local\\Packages\\Microsoft\.MicrosoftEdge_[0-9A-z]{0,3}\\AC\\[^\\]+\\MicrosoftEdge\\Cache",
          "last_active_session": [
              r"Users\\[^\\]+\\AppData\\Local\\Packages\\Microsoft\.MicrosoftEdge_[0-9A-z]{0,60}\\AC\\MicrosoftEdge\\User\\Default\\Recovery\\Active$"]
      }
  }
