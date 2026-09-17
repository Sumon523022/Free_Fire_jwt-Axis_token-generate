# TEAMX JWT API — Usage Guide

এই প্রজেক্টটি Flask ভিত্তিক একটি API। এটি `uid/password` থেকে OAuth token সংগ্রহ করে এবং `access_token` ব্যবহার করে JWT response তৈরি করার চেষ্টা করে।

> **নোট:** API-টি শুধুমাত্র নিজের/অনুমোদিত অ্যাকাউন্ট ও বৈধ ব্যবহারের জন্য ব্যবহার করুন। Access token, password, cookie বা secret কখনো public repository-তে প্রকাশ করবেন না।

## 📁 Project Files

| File | কাজ |
|---|---|
| `app.py` | মূল Flask API |
| `my_pb2.py` | GameData protobuf definition |
| `output_pb2.py` | API response protobuf definition |
| `requirements.txt` | Python dependencies |
| `vercel.json` | Vercel deployment configuration |
| `README.md` | এই usage guide |

## ⚙️ Installation

Python environment-এ project directory-তে গিয়ে:

```bash
pip install -r requirements.txt
```

Termux-এ প্রয়োজনীয় package install করার পর:

```bash
python app.py
```

API server চালু হলে default port:

```text
1080
```

Local address:

```text
http://127.0.0.1:1080
```

## 🔑 API Endpoints

### 1. `/token`

এই endpoint `uid` এবং `password` নেয় এবং OAuth flow-এর মাধ্যমে পরবর্তী JWT generation process চালায়।

**Method:** `GET`

**Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `uid` | Yes | অনুমোদিত account UID |
| `password` | Yes | সংশ্লিষ্ট account credential |

**Example:**

```text
http://127.0.0.1:1080/token?uid=YOUR_UID&password=YOUR_PASSWORD
```

**Missing parameter হলে:**

```json
{
  "message": "Missing uid or password"
}
```

## 2. `/access-jwt`

এই endpoint `access_token` নেয়। চাইলে `open_id` সরাসরি দেওয়া যায়; না দিলে API নিজে সেটি resolve করার চেষ্টা করে।

**Method:** `GET`

### Option A — access_token only

```text
http://127.0.0.1:1080/access-jwt?access_token=YOUR_ACCESS_TOKEN
```

### Option B — access_token + open_id

```text
http://127.0.0.1:1080/access-jwt?access_token=YOUR_ACCESS_TOKEN&open_id=YOUR_OPEN_ID
```

**Required:**

- `access_token`

**Optional:**

- `open_id`

## 📦 Success Response

সফল হলে response-এ সাধারণত নিচের ধরনের তথ্য থাকতে পারে:

```json
{
  "account_id": "...",
  "account_name": "...",
  "open_id": "...",
  "access_token": "...",
  "platform": "...",
  "region": "...",
  "status": "success",
  "token": "..."
}
```

`token` হলো server response থেকে পাওয়া JWT value।

## ❌ Common Errors

### Missing access token

```json
{
  "message": "missing access_token"
}
```

### Missing UID/password

```json
{
  "message": "Missing uid or password"
}
```

### Open ID পাওয়া যায়নি

```json
{
  "message": "Failed to extract open_id"
}
```

অথবা:

```json
{
  "message": "Failed to extract open_id"
}
```

### কোনো valid platform পাওয়া যায়নি

```json
{
  "message": "No valid platform found"
}
```

## 🧪 Quick Test

Server চালু করার পর browser বা curl দিয়ে endpoint পরীক্ষা করা যায়।

```bash
curl "http://127.0.0.1:1080/access-jwt?access_token=YOUR_ACCESS_TOKEN"
```

অথবা:

```bash
curl "http://127.0.0.1:1080/access-jwt?access_token=YOUR_ACCESS_TOKEN&open_id=YOUR_OPEN_ID"
```

## 🌐 Vercel Deployment

প্রজেক্টে `vercel.json` দেওয়া আছে এবং `app.py` entry point হিসেবে ব্যবহার করা হয়েছে।

Deploy করার আগে নিশ্চিত করুন:

1. `requirements.txt` সঠিক আছে।
2. `app.py`, `my_pb2.py`, এবং `output_pb2.py` একই project directory-তে আছে।
3. কোনো password, cookie, API secret বা access token public source code-এ রাখা হয়নি।
4. Deployment environment-এ প্রয়োজনীয় secret নিরাপদ environment variable হিসেবে রাখা হয়েছে।

## 🔒 Security

এই project-এর source code-এ credential বা session information hard-code করা থাকলে deployment/public sharing-এর আগে সেগুলো পরিবর্তন বা সরিয়ে ফেলুন।

বিশেষ করে:

- Account password
- Access token
- Session cookie
- Client secret
- Private API key

এগুলো GitHub, public ZIP বা public Vercel source-এ প্রকাশ করবেন না।

## 📌 Important

- API response সবসময় সফল নাও হতে পারে।
- External service/API পরিবর্তন হলে endpoint কাজ করা বন্ধ করতে পারে।
- HTTP status code এবং JSON response দেখে error handle করুন।
- Production ব্যবহারের আগে authentication, rate limiting এবং secret management যোগ করা উচিত।

## 👨‍💻 Project Structure

```text
TEAMX-JWT-API-OB55/
├── app.py
├── my_pb2.py
├── output_pb2.py
├── requirements.txt
├── vercel.json
└── README.md
```

---

### Maintainer

**TEAM X**

Version: **OB55**

