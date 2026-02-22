const BASE_URL = 'https://wosdev.randomchaoslabs.com';

/**
 * Direct API helper for test setup and teardown.
 * Uses fetch to call the backend directly, bypassing the UI.
 */
export class ApiHelper {
  constructor(private token: string) {}

  private headers() {
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.token}`,
    };
  }

  async addHero(name: string, data: Record<string, any> = {}) {
    const res = await fetch(
      `${BASE_URL}/api/heroes/${encodeURIComponent(name)}`,
      { method: 'PUT', headers: this.headers(), body: JSON.stringify(data) }
    );
    if (!res.ok) throw new Error(`Failed to add hero ${name}: ${res.status}`);
    return res.json();
  }

  async removeHero(name: string) {
    const res = await fetch(
      `${BASE_URL}/api/heroes/${encodeURIComponent(name)}`,
      { method: 'DELETE', headers: this.headers() }
    );
    if (!res.ok && res.status !== 404) {
      throw new Error(`Failed to remove hero ${name}: ${res.status}`);
    }
  }

  async getOwnedHeroes() {
    const res = await fetch(`${BASE_URL}/api/heroes/owned`, {
      headers: this.headers(),
    });
    if (!res.ok) throw new Error(`Failed to get heroes: ${res.status}`);
    return res.json();
  }

  async createProfile(name: string, data: Record<string, any> = {}) {
    const res = await fetch(`${BASE_URL}/api/profiles`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({ name, ...data }),
    });
    if (!res.ok)
      throw new Error(`Failed to create profile: ${res.status}`);
    return res.json();
  }

  async deleteProfile(profileId: string, hard = true) {
    const res = await fetch(
      `${BASE_URL}/api/profiles/${profileId}?hard=${hard}`,
      { method: 'DELETE', headers: this.headers() }
    );
    if (!res.ok && res.status !== 404) {
      throw new Error(`Failed to delete profile: ${res.status}`);
    }
  }

  async listProfiles() {
    const res = await fetch(`${BASE_URL}/api/profiles`, {
      headers: this.headers(),
    });
    if (!res.ok) throw new Error(`Failed to list profiles: ${res.status}`);
    return res.json();
  }

  async deleteAnnouncement(id: string) {
    const res = await fetch(`${BASE_URL}/api/admin/announcements/${id}`, {
      method: 'DELETE',
      headers: this.headers(),
    });
    if (!res.ok && res.status !== 404) {
      throw new Error(`Failed to delete announcement: ${res.status}`);
    }
  }
}
