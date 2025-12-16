import { createContext, useContext, useState, useEffect } from "react";
import api from "../lib/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Загружаем пользователя из localStorage при монтировании
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const savedUser = localStorage.getItem("user");
    
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
        // Проверяем валидность токена
        verifyToken();
      } catch (error) {
        console.error("Failed to parse user from localStorage", error);
        logout();
      }
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async () => {
    try {
      const response = await api.post("/api/v1/login/test-token");
      setUser(response.data);
      localStorage.setItem("user", JSON.stringify(response.data));
      setLoading(false);
    } catch (error) {
      console.error("Token verification failed", error);
      logout();
    }
  };

  const login = async (email, password) => {
    try {
      // OAuth2 требует application/x-www-form-urlencoded
      const params = new URLSearchParams();
      params.append("username", email); // OAuth2 использует username вместо email
      params.append("password", password);

      const response = await api.post("/api/v1/login/access-token", params.toString(), {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const { access_token } = response.data;
      localStorage.setItem("access_token", access_token);

      // Получаем данные пользователя
      const userResponse = await api.post("/api/v1/login/test-token");
      setUser(userResponse.data);
      localStorage.setItem("user", JSON.stringify(userResponse.data));

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Login failed",
      };
    }
  };

  const register = async (email, password, fullName) => {
    try {
      const response = await api.post("/api/v1/users/signup", {
        email,
        password,
        full_name: fullName || null,
      });

      // После регистрации автоматически логинимся
      return await login(email, password);
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Registration failed",
      };
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setUser(null);
  };

  const updateUser = (updatedUser) => {
    setUser(updatedUser);
    localStorage.setItem("user", JSON.stringify(updatedUser));
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
    isSuperuser: user?.is_superuser ?? false,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

