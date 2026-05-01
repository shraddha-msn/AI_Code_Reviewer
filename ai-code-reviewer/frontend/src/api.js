import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 120000,
});

export async function createReview(repoUrl) {
  const { data } = await api.post("/review", { repo_url: repoUrl });
  return data;
}

export async function listReviews() {
  const { data } = await api.get("/reviews");
  return data;
}

export async function getReview(id) {
  const { data } = await api.get(`/reviews/${id}`);
  return data;
}
