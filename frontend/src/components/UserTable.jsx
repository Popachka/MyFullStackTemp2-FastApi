export default function UserTable({ users, onEdit, onDelete }) {
  if (users.length === 0) {
    return <div className="empty-state">No users found</div>;
  }

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Email</th>
            <th>Full Name</th>
            <th>Active</th>
            <th>Superuser</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.email}</td>
              <td>{user.full_name || "-"}</td>
              <td>
                <span className={`badge ${user.is_active ? "badge-success" : "badge-error"}`}>
                  {user.is_active ? "Yes" : "No"}
                </span>
              </td>
              <td>
                {user.is_superuser && (
                  <span className="badge badge-superuser">Yes</span>
                )}
              </td>
              <td>
                <div className="table-actions">
                  <button
                    onClick={() => onEdit(user)}
                    className="btn-sm btn-edit"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(user.id)}
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

