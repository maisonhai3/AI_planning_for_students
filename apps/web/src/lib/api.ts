const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface GenerateResponse {
  success: boolean;
  plan: object;
  html: string;
  error?: string;
  code?: string;
}

export interface SaveResponse {
  success: boolean;
  id: string;
  share_url: string;
}

export interface FeedbackPayload {
  plan_id: string;
  action: 'save' | 'regenerate' | 'share';
}

export async function generatePlan(input: string): Promise<GenerateResponse> {
  const response = await fetch(`${API_URL}/api/v1/generate/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ input }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Failed to generate plan');
  }

  return data;
}

export async function savePlan(planData: object, html: string): Promise<SaveResponse> {
  const response = await fetch(`${API_URL}/api/v1/plans/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ plan: planData, html }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Failed to save plan');
  }

  return data;
}

export async function getPlan(id: string): Promise<{ plan: object; html: string }> {
  const response = await fetch(`${API_URL}/api/v1/plans/${id}/`);

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Plan not found');
  }

  return data;
}

export async function trackFeedback(payload: FeedbackPayload): Promise<void> {
  await fetch(`${API_URL}/api/v1/feedback/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}
