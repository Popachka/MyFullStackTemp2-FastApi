import { useState, useEffect } from "react";
import api from "../lib/axios";
import ItemForm from "../components/ItemForm";
import ItemTable from "../components/ItemTable";

export default function ItemsPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const response = await api.get("/api/v1/items/");
      setItems(response.data.data || []);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load items");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleCreate = () => {
    setEditingItem(null);
    setShowForm(true);
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setShowForm(true);
  };

  const handleDelete = async (itemId) => {
    if (!window.confirm("Are you sure you want to delete this item?")) {
      return;
    }

    try {
      await api.delete(`/api/v1/items/${itemId}`);
      fetchItems();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete item");
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingItem(null);
  };

  const handleFormSuccess = () => {
    fetchItems();
    handleFormClose();
  };

  if (loading) {
    return <div className="loading">Loading items...</div>;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Items Management</h1>
        <button onClick={handleCreate} className="btn-primary">
          Create Item
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showForm && (
        <ItemForm
          item={editingItem}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}

      <ItemTable items={items} onEdit={handleEdit} onDelete={handleDelete} />
    </div>
  );
}

