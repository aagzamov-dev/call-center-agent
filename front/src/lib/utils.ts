import { format, formatDistanceToNow } from 'date-fns';

export function cn(...classes: (string | false | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function formatDate(iso: string): string {
  if (!iso) return '';
  try { return format(new Date(iso), 'MMM d, HH:mm:ss'); } catch { return iso; }
}

export function timeAgo(iso: string): string {
  if (!iso) return '';
  try { return formatDistanceToNow(new Date(iso), { addSuffix: true }); } catch { return iso; }
}

export function severityClass(severity: string): string {
  return `badge-${severity || 'info'}`;
}
