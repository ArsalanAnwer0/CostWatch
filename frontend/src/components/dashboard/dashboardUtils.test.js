import { getInitials, PROVIDER_LABELS } from './dashboardUtils';

describe('dashboardUtils', () => {
  it('maps provider keys to readable labels', () => {
    expect(PROVIDER_LABELS.aws).toBe('AWS');
    expect(PROVIDER_LABELS.azure).toBe('Azure');
    expect(PROVIDER_LABELS.gcp).toBe('GCP');
  });

  it('builds initials from a user full name', () => {
    expect(getInitials({ full_name: 'Taylor Nguyen' })).toBe('TN');
  });

  it('falls back to email initials when a name is not available', () => {
    expect(getInitials({ email: 'owner@costwatch.com' })).toBe('OW');
  });

  it('returns the product fallback when no user details exist', () => {
    expect(getInitials(null)).toBe('CW');
  });
});
