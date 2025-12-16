import { useState, useEffect } from "react";
import api from "../lib/axios";
import { useAuth } from "../contexts/AuthContext";

export default function TelegramConnection() {
  const { user, updateUser } = useAuth();
  const [token, setToken] = useState("");
  const [botUsername, setBotUsername] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    // Загружаем информацию о боте при монтировании компонента
    const fetchBotInfo = async () => {
      try {
        const response = await api.get("/api/v1/utils/bot-info");
        if (response.data.enabled && response.data.username) {
          setBotUsername(response.data.username);
        }
        // Если бот настроен, но username не получен (сетевые проблемы),
        // используем fallback значение
      } catch (err) {
        console.error("Failed to fetch bot info", err);
        // При ошибке используем fallback значение
      }
    };
    fetchBotInfo();
  }, []);

  const isConnected = !!user?.telegram_id;

  const generateToken = async () => {
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await api.post("/api/v1/users/me/telegram/token");
      setToken(response.data.token);
      setSuccess("Токен сгенерирован! Используйте его в течение 10 минут.");
    } catch (err) {
      setError(err.response?.data?.detail || "Не удалось сгенерировать токен");
    } finally {
      setLoading(false);
    }
  };

  const disconnectTelegram = async () => {
    if (!window.confirm("Вы уверены, что хотите отвязать Telegram аккаунт?")) {
      return;
    }

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await api.delete("/api/v1/users/me/telegram");
      // Обновляем пользователя через GET /me
      const userResponse = await api.get("/api/v1/users/me");
      updateUser(userResponse.data);
      setSuccess("Telegram аккаунт успешно отвязан");
      setToken("");
    } catch (err) {
      setError(err.response?.data?.detail || "Не удалось отвязать аккаунт");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!token) return;
    const username = botUsername || import.meta.env.VITE_TELEGRAM_BOT_USERNAME || "topedik_bot";
    const botUrl = `https://t.me/${username.replace("@", "")}/start?start=${token}`;
    navigator.clipboard.writeText(botUrl).then(() => {
      setSuccess("Ссылка скопирована в буфер обмена!");
    });
  };

  const copyToken = () => {
    if (!token) return;
    navigator.clipboard.writeText(token).then(() => {
      setSuccess("Токен скопирован в буфер обмена!");
    });
  };

  return (
    <div className="telegram-section">
      <h2>Telegram подключение</h2>
      
      {isConnected ? (
        <div className="telegram-connected">
          <div className="status-badge status-connected">
            ✓ Подключено
          </div>
          <p>Ваш Telegram ID: <strong>{user.telegram_id}</strong></p>
          <button
            onClick={disconnectTelegram}
            disabled={loading}
            className="btn-secondary"
          >
            {loading ? "Отвязывание..." : "Отвязать Telegram"}
          </button>
        </div>
      ) : (
        <div className="telegram-disconnected">
          <div className="status-badge status-disconnected">
            ✗ Не подключено
          </div>
          <p>
            Подключите свой Telegram аккаунт для использования бота.
            Токен действителен в течение 10 минут.
          </p>
          
          {!token ? (
            <button
              onClick={generateToken}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? "Генерация..." : "Сгенерировать токен"}
            </button>
          ) : (
            <div className="token-display">
              <div className="token-info">
                <p><strong>Токен сгенерирован!</strong></p>
                <p className="token-hint">
                  Откройте Telegram и перейдите по ссылке ниже или отправьте токен боту:
                </p>
                <div className="token-box">
                  <code className="token-value">{token}</code>
                  <button onClick={copyToken} className="btn-sm btn-copy">
                    Копировать
                  </button>
                </div>
                <div className="telegram-link-box">
                  <a
                    href={`https://t.me/${(botUsername || import.meta.env.VITE_TELEGRAM_BOT_USERNAME || "topedik_bot").replace("@", "")}/start?start=${token}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="telegram-link"
                  >
                    Открыть в Telegram
                  </a>
                  <button onClick={copyToClipboard} className="btn-sm btn-copy">
                    Копировать ссылку
                  </button>
                </div>
                <button
                  onClick={() => {
                    setToken("");
                    setSuccess("");
                  }}
                  className="btn-secondary"
                  style={{ marginTop: "1rem" }}
                >
                  Сгенерировать новый токен
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
    </div>
  );
}

