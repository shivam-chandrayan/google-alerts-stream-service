# **MegaFeed**

A frontend application built with **Vite**, **React**, and **TypeScript**.
Add multiple Google Alerts RSS Feed and see all alerts in one place.

[Demo Link](https://google-alerts-stream-web-git-50c1d8-shivam-chandrayans-projects.vercel.app/ "Demo Link")

## **Features**
- Manage multiple RSS feeds easily
- Bookmark entries
- Auto update alerts

---

## **Getting Started**

### **Prerequisites**
Ensure you have the following installed on your machine:
- **Node.js** (version 16 or later)
- **npm** or **yarn**

---

### **Installation**

1. Clone the repository:
   ```bash
   gh repo clone shivam-chandrayan/google-alerts-stream-service
   cd google-alerts-stream-service
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

---

### **Running the Application**

To start the development server:
```bash
npm run dev
# or
yarn dev
```
---

### **Building the Application**

To build the app for production:
```bash
npm run build
# or
yarn build
```

The build output will be available in the `dist/` directory.

---

### **Environment Variables**

This project uses environment variables for configuration. Ensure the following variables are defined in a `.env` file:
```env
VITE_API_BASE_URL=https://your-api-base-url.com
```

---

## **Deployment**

This project can be deployed to any static hosting provider (e.g., Vercel, Netlify).

Example deployment on Vercel:
1. Push your code to a GitHub repository.
2. Link the repo to your Vercel account.
3. Set the environment variables in the Vercel dashboard.
4. Deploy!

---

## **License**

This project is licensed under the [MIT License](LICENSE).
