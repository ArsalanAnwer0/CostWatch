export const PROVIDER_LABELS = {
  aws: 'AWS',
  azure: 'Azure',
  gcp: 'GCP',
};

export function getInitials(user) {
  const name = user?.full_name || user?.name;

  if (name) {
    return name
      .split(' ')
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join('');
  }

  return user?.email?.slice(0, 2).toUpperCase() || 'CW';
}
