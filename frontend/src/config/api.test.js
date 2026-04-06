import { DEFAULT_HEADERS, getAuthHeaders, getAuthToken } from './api';

describe('api config helpers', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('reads the primary auth token key first', () => {
    window.localStorage.setItem('token', 'primary-token');
    window.localStorage.setItem('auth_token', 'secondary-token');

    expect(getAuthToken()).toBe('primary-token');
  });

  it('falls back to the legacy auth token key', () => {
    window.localStorage.setItem('auth_token', 'legacy-token');

    expect(getAuthToken()).toBe('legacy-token');
  });

  it('builds auth headers when a token exists', () => {
    window.localStorage.setItem('token', 'secret-token');

    expect(getAuthHeaders()).toEqual({
      ...DEFAULT_HEADERS,
      Authorization: 'Bearer secret-token',
    });
  });

  it('returns default headers when there is no token', () => {
    expect(getAuthHeaders()).toEqual(DEFAULT_HEADERS);
  });
});
