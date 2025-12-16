export default function ItemTable({ items, onEdit, onDelete }) {
  if (items.length === 0) {
    return <div className="empty-state">No items found. Create your first item!</div>;
  }

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>{item.title}</td>
              <td>{item.description || "-"}</td>
              <td>
                <div className="table-actions">
                  <button
                    onClick={() => onEdit(item)}
                    className="btn-sm btn-edit"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(item.id)}
                    className="btn-sm btn-delete"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

