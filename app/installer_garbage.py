AVAILABLE_APPS = {
    "Launcher Games": {
        "steam": {
            "url_64": "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe",
            "url_32": "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe"
        },
        "epic_games": {
            "url_64": "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi",
            "url_32": "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi"
        },
        "ubisoft_connect": {
            "url_64": "https://ubi.li/4vxt9",
            "url_32": "https://ubi.li/4vxt9"
        }
    },
    
    "Communication & Voice Chat": {
        "discord": {
            "url_64": "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64",
            "url_32": "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x86"
        },
        "teamspeak": {
            "url_64": "https://files.teamspeak-services.com/pre_releases/client/6.0.0-beta2/teamspeak-client.msi",
            "url_32": "https://files.teamspeak-services.com/pre_releases/client/6.0.0-beta2/teamspeak-client.msi" # Asumsikan link sama jika 32-bit tidak ada
        }
    },

    "Web Browsers": {
        "firefox": {
            "url_64": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=id",
            "url_32": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win&lang=id"
        },
        "chrome": {
            "url_64": "https://dl.google.com/chrome/install/standalonesetup64.exe",
            "url_32": "https://dl.google.com/chrome/install/standalonesetup.exe"
        }
    },
    
    "IDE & Code Editors": {
        "vscode": {
            "url_64": "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user",
            "url_32": "https://code.visualstudio.com/sha/download?build=stable&os=win32-user"
        },
        "sublime_text": {
            "url_64": "https://download.sublimetext.com/sublime_text_build_4169_x64_setup.exe",
            "url_32": "https://download.sublimetext.com/sublime_text_build_4169_setup.exe"
        }
    },

    "Media Players": {
        "vlc": {
            "url_64": "https://get.videolan.org/vlc/last/win64/",
            "url_32": "https://get.videolan.org/vlc/last/win32/"
        },
        "kmplayer": {
            "url_64": "https://update.kmplayer.com/player/download/kmp64",
            "url_32": "https://update.kmplayer.com/player/download/kmp"
        }
    }
}