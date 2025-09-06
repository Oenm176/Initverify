<div align="center">
  
  <h1 align="center">InitVerify - CLI Installer</h1>
  
  <p align="center">
    An interactive CLI-style desktop application to automate downloading and installing your favorite Windows applications.
    <br />
    <a href="#-key-features"><strong>View Features »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Oenm176/Initverify/issues">Report Bug</a>
    ·
    <a href="https://github.com/Oenm176/Initverify/issues">Request Feature</a>
  </p>
</div>

<div align="center">
  <a href="https://github.com/Oenm176/Initverify/stargazers"><img src="https://img.shields.io/github/stars/Oenm176/Initverify?style=for-the-badge" alt="Stars"></a>
  <a href="https://github.com/Oenm176/Initverify/network/members"><img src="https://img.shields.io/github/forks/Oenm176/Initverify?style=for-the-badge" alt="Forks"></a>
  <a href="https://github.com/Oenm176/Initverify/issues"><img src="https://img.shields.io/github/issues/Oenm176/Initverify?style=for-the-badge" alt="Open Issues"></a>
  <a href="https://github.com/Oenm176/Initverify/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Oenm176/Initverify?style=for-the-badge" alt="License"></a>
</div>

<br>

![InitVerify Screenshot](https://i.imgur.com/kS5zL5C.png)


## 📝 About The Project

InitVerify is a utility designed to simplify the process of setting up a new computer or reinstalling applications. Built with Python and PySide6, this application provides a modern and interactive terminal-style interface, allowing users to efficiently select and install popular applications directly from their official sources.

The project also comes with advanced features like dynamic application list updates from the internet and automatic notifications for new versions, making it a tool that is always up-to-date.

### 🛠️ Built With

* ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
* ![PySide6](https://img.shields.io/badge/PySide6-249392?style=for-the-badge&logo=qt&logoColor=white)
* ![Requests](https://img.shields.io/badge/Requests-2.31.0-orange?style=for-the-badge)


## ✨ Key Features

* **CLI-Style Interface**: Fast and efficient interaction through text commands.
* **Shopping Cart Management**: Select multiple applications and install them all at once.
* **Dynamic Application List**: The list of installable apps is always updated automatically from an online source.
* **Update Notifications**: Notifies you when a new version of InitVerify is available.
* **Online Status Indicator**: Provides instant visual feedback on internet connectivity.
* **Advanced Progress Bar**: Track the download process with speed and ETA information.
* **Portable**: No installation required. Just extract and run.

---

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Python 3.8+
* Git

### Installation Guide

1.  **Clone the repo:**
    ```sh
    git clone [https://github.com/Oenm176/Initverify.git](https://github.com/Oenm176/Initverify.git)
    cd Initverify
    ```

2.  **Create and activate a virtual environment (venv):**
    ```sh
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install all dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **URL Configuration**:
    Open the `app/logic.py` file and replace the placeholder values for `APP_LIST_URL` and `VERSION_CHECK_URL` with the Raw URLs from your Gist and `version.json` file in your repository.

## 🏃 Usage

Run the application using the launcher script to ensure Administrator privileges are granted:
```sh
python run.py
```
The application will request UAC confirmation; click "Yes" to continue.

### Available Commands
```
help         : Displays all available commands.
show-apps    : Shows the list of installable applications.
add          : Adds one or more apps to the cart.
remove       : Removes one or more apps from the cart.
remove-all   : Clears the entire cart.
cart         : Shows the current contents of the cart.
install      : Starts the installation process.
clear        : Clears the output screen.
restart      : Restarts the application.
```

---

## 🗺️ Roadmap

* [ ] Implement GitHub Actions for automated builds and releases.
* [ ] Add more applications to the list.
* [ ] Self-updating system for the core application.

See the [open issues](https://github.com/Oenm176/Initverify/issues) for a full list of proposed features (and known issues).

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE.txt` for more information.


## ☕ Support This Project

If you find this application useful and wish to support its future development, you can buy me a coffee! Every contribution is greatly appreciated.

<p align="left">
  <a href='https://ko-fi.com/V7V51KTW8I' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi5.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
</p>

---