# 🔐 SecureVault

A comprehensive password and credential management system built with Flask and MySQL, designed to securely store and manage sensitive information with military-grade encryption.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Security Features](#security-features)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [License](#license)

## ✨ Features

### 🛡️ Multi-Vault Storage
- **Password Vault**: Securely store website credentials with website URL and username
- **Card Vault**: Safely manage payment card information with expiry tracking
- **Notes Vault**: Store sensitive notes and personal information
- **API Vault**: Manage API keys and tokens with encryption

### 🔐 Advanced Security
- **Fernet Encryption**: Military-grade symmetric encryption for sensitive data
- **Bcrypt Hashing**: Industry-standard password hashing for master passwords
- **OTP Verification**: Email-based one-time password for password changes
- **Password Strength Analysis**: Real-time password strength evaluation (Weak/Medium/Strong)
- **Session Management**: Secure user session handling with automatic logout

### 👤 User Management
- User registration with email verification
- Secure login with bcrypt password verification
- Profile settings and account customization
- OTP-based password reset functionality
- User dashboard with comprehensive statistics

### 📊 Dashboard Analytics
- Total credential count across all vaults
- Password strength analysis with scoring system
- Vault creation dates and last modified timestamps
- Visual grade system (Excellent/Good/Moderate/Weak)
- Quick access to recently added credentials

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.x, Flask |
| **Database** | MySQL 5.7+ |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Encryption** | Fernet (cryptography library), Bcrypt |
| **Email Service** | SMTP (Gmail) |

## 📦 Prerequisites

- Python 3.7 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)
- Gmail account with App Password (for OTP emails)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/Psi-gh-11/SecureVault.git
cd SecureVault
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install flask cryptography python-dotenv mysql-connector-python bcrypt
```

4. **Create MySQL database**
```sql
CREATE DATABASE SecureVaultDB;

USE SecureVaultDB;

CREATE TABLE Users (
    User_ID INT PRIMARY KEY AUTO_INCREMENT,
    User_Name VARCHAR(100),
    User_Email VARCHAR(100) UNIQUE,
    User_Password LONGTEXT,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE WebsiteVault (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    User INT,
    Website_URL VARCHAR(255),
    Username VARCHAR(255),
    Password LONGTEXT,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (User) REFERENCES Users(User_ID)
);

CREATE TABLE CardVault (
    CNO INT PRIMARY KEY AUTO_INCREMENT,
    User INT,
    CardHolder VARCHAR(255),
    CardNo VARCHAR(255),
    Expiry VARCHAR(10),
    Remainder VARCHAR(255),
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (User) REFERENCES Users(User_ID)
);

CREATE TABLE NoteVault (
    NoteNo INT PRIMARY KEY AUTO_INCREMENT,
    User INT,
    Notes LONGTEXT,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (User) REFERENCES Users(User_ID)
);

CREATE TABLE ApiVault (
    APINo INT PRIMARY KEY AUTO_INCREMENT,
    User INT,
    Service VARCHAR(255),
    API_Key LONGTEXT,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (User) REFERENCES Users(User_ID)
);
```

## ⚙️ Configuration

1. **Generate Fernet Key**
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

2. **Create `.env` file**
```env
FERNET_KEY=your_generated_key_here
```

3. **Update database credentials in `vault.py`**
```python
db = mysql.connector.connect(
    host="localhost",
    user="root",           # Your MySQL username
    password="password123", # Your MySQL password
    database="SecureVaultDB"
)
```

4. **Configure Gmail App Password** (for OTP emails)
- Enable 2-factor authentication on your Gmail account
- Generate an app-specific password
- Update credentials in `vault.py` (lines 140-141):
```python
sender_email = "your_email@gmail.com"
app_password = "your_app_password"
```

## 📖 Usage

1. **Start the application**
```bash
python vault.py
```

2. **Access the application**
- Open your browser and navigate to `http://localhost:5000`
- Create a new account or login with existing credentials

3. **Main Features**
- **Dashboard**: View vault statistics and password strength analysis
- **Password Vault**: Add, update, and delete website credentials
- **Card Vault**: Manage payment card information
- **Notes Vault**: Store sensitive notes
- **API Vault**: Secure API key storage
- **Settings**: Update profile and change master password (with OTP verification)

## 📁 Project Structure

```
SecureVault/
├── vault.py                 # Main Flask application
├── .env                     # Environment variables (Fernet key)
├── static/
│   ├── styles.css          # CSS styling
│   ├── script.js           # Frontend JavaScript
│   └── img{1-7}.jpg        # UI images
└── templates/
    ├── home.html           # Landing page
    ├── signup.html         # Registration page
    ├── login.html          # Login page
    ├── dashboard.html      # Main dashboard
    ├── settings.html       # User settings
    ├── vault.html          # Vault management interface
    └── vault-details.html  # Detailed vault view
```

## 🔒 Security Features

### Encryption
- **Fernet Symmetric Encryption**: All sensitive data (passwords, API keys) encrypted with AES-128
- **Bcrypt Hashing**: Master passwords hashed with salt rounds for protection against rainbow tables

### Password Requirements
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (!@#$%^&*(),.?":{}|<>)

### Additional Security
- **Session-based authentication**: Secure session tokens
- **OTP verification**: Email-based one-time passwords for password changes
- **Input validation**: SQL injection prevention with parameterized queries
- **HTTPS-ready**: Compatible with SSL/TLS deployment

### Password Strength Scoring
- **Excellent** (≥80): Strong, secure passwords
- **Good** (60-79): Adequate security
- **Moderate** (40-59): Acceptable but improvable
- **Weak** (<40): Needs improvement

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET, POST | `/signup` | User registration |
| GET, POST | `/login` | User login |
| GET | `/dashboard` | Main dashboard |
| GET | `/settings` | User settings page |
| POST | `/save` | Update user profile |
| POST | `/send-otp` | Send OTP for password reset |
| POST | `/verify` | Verify OTP |
| POST | `/change` | Change master password |
| POST | `/password-vault` | Add website credential |
| POST | `/card-vault` | Add card information |
| POST | `/note-vault` | Add note |
| POST | `/api-vault` | Add API key |
| GET | `/vault-details` | View all vault items |
| POST | `/update/password/<id>` | Update website credential |
| POST | `/update/card/<id>` | Update card info |
| POST | `/update/note/<id>` | Update note |
| POST | `/update/api/<id>` | Update API key |
| POST | `/delete_website/<id>` | Delete website credential |
| POST | `/delete_card/<id>` | Delete card |
| POST | `/delete_note/<id>` | Delete note |
| POST | `/delete_api/<id>` | Delete API key |
| GET | `/logout` | User logout |

## 💾 Database Schema

### Users Table
- `User_ID`: Primary key
- `User_Name`: User's name
- `User_Email`: Email address (unique)
- `User_Password`: Bcrypt-hashed master password
- `Created_At`: Account creation timestamp
- `Updated_At`: Last update timestamp

### WebsiteVault Table
- `ID`: Primary key
- `User`: Foreign key to Users
- `Website_URL`: Website address
- `Username`: Login username
- `Password`: Fernet-encrypted password
- `Created_At`, `Updated_At`: Timestamps

### CardVault Table
- `CNO`: Primary key
- `User`: Foreign key to Users
- `CardHolder`: Cardholder name
- `CardNo`: Encrypted card number
- `Expiry`: Card expiration date
- `Remainder`: Additional notes
- `Created_At`, `Updated_At`: Timestamps

### NoteVault Table
- `NoteNo`: Primary key
- `User`: Foreign key to Users
- `Notes`: Encrypted note content
- `Created_At`, `Updated_At`: Timestamps

### ApiVault Table
- `APINo`: Primary key
- `User`: Foreign key to Users
- `Service`: Service/platform name
- `API_Key`: Fernet-encrypted API key
- `Created_At`, `Updated_At`: Timestamps

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to fork this repository and submit pull requests for any improvements.

## ⚠️ Security Notice

This is an educational project. While it implements industry-standard security practices, for production use, consider:
- Deploying with HTTPS/SSL
- Using environment variables for all credentials
- Implementing rate limiting
- Adding two-factor authentication (2FA)
- Regular security audits and penetration testing
- Compliance with data protection regulations (GDPR, etc.)

---

**Made with ❤️ for secure credential management**
