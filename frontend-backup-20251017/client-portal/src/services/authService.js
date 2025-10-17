import axiosInstance from "../utils/axiosInstance";

export const login = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const response = await axiosInstance.post("/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  if (response.data.access_token) {
    localStorage.setItem("access_token", response.data.access_token);
  }

  return response.data;
};

export const register = async (email, password, full_name) => {
  const response = await axiosInstance.post("/auth/register", {
    email,
    password,
    full_name,
  });
  return response.data;
};
