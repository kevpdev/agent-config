function renderBadge(user) {
  const tone = user.active ? 'badge--on' : 'badge--off';
  return `
    <span class="badge ${tone}">
      <img src="${user.avatarUrl}" alt="" />
      <strong>${user.displayName}</strong>
      <em>${user.roleLabel}</em>
    </span>
  `;
}
