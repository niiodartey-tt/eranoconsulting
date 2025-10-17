import { api } from './api';
import Cookies from 'js-cookie';

export async function login(email: string, password: string) {
  const res = await api.post('/auth/login', { email, password });
  console.log('Login response:', res.data); // 🧩 Add this line
  Cookies.set('token', res.data.access_token);
  return res.data;
}


export async function register(email: string, password: string, full_name: string) {
  return await api.post('/auth/register', { email, password, full_name });
}

export function logout() {
  Cookies.remove('token');
}
