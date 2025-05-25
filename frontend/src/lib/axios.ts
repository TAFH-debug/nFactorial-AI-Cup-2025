import axios from "axios";

const api = axios.create({
    baseURL: `https://${process.env.NEXT_PUBLIC_API_URL}`,
});

export default api;

