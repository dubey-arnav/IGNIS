import axios from "axios";

const apiBase =
  import.meta.env.VITE_API_BASE_URL !== undefined
    ? import.meta.env.VITE_API_BASE_URL
    : "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: apiBase,
  timeout: 20000,
});

export default client;
