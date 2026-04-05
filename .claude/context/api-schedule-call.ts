/**
 * API Endpoint: Schedule Scoping Call
 * POST /api/schedule-call
 *
 * Saves scheduling information and returns phone number to call
 */

import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export interface ScheduleCallRequest {
  name: string;
  email: string;
  phone?: string;
  company?: string;
  timezone: string;
  time_slot: string;
  scheduled_time: string;
}

export interface ScheduleCallResponse {
  success: boolean;
  session_id: string;
  phone_number: string;
  scheduled_time: string;
  confirmation_email_sent: boolean;
}

// Your ElevenLabs phone number (configure in ElevenLabs dashboard)
const ELEVENLABS_PHONE_NUMBER = '+1-555-CALL-01'; // Replace with your actual number

/**
 * POST /api/schedule-call
 * Schedule a new scoping call
 */
export async function POST(request: Request): Promise<Response> {
  try {
    const data: ScheduleCallRequest = await request.json();

    // Validate required fields
    if (!data.name || !data.email || !data.timezone) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields' }),
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
      return new Response(
        JSON.stringify({ error: 'Invalid email format' }),
        { status: 400 }
      );
    }

    // Calculate scheduled datetime
    const scheduledTime = new Date(data.scheduled_time);

    // Save to Supabase
    const { data: session, error } = await supabase
      .from('scoping_sessions')
      .insert({
        user_name: data.name,
        email: data.email,
        phone: data.phone || '',
        scheduled_time: scheduledTime.toISOString(),
        status: 'scheduled'
      })
      .select()
      .single();

    if (error) {
      console.error('Supabase error:', error);
      return new Response(
        JSON.stringify({ error: 'Failed to schedule call' }),
        { status: 500 }
      );
    }

    // Send confirmation email to user
    try {
      await sendConfirmationEmail(data.name, data.email, ELEVENLABS_PHONE_NUMBER, scheduledTime);
    } catch (emailError) {
      console.error('Email error:', emailError);
      // Don't fail the entire request if email fails
    }

    // Send notification to team
    try {
      await notifyTeam(data.name, data.email, data.company, scheduledTime);
    } catch (notifyError) {
      console.error('Notification error:', notifyError);
      // Don't fail the entire request
    }

    return new Response(
      JSON.stringify({
        success: true,
        session_id: session.id,
        phone_number: ELEVENLABS_PHONE_NUMBER,
        scheduled_time: scheduledTime.toISOString(),
        confirmation_email_sent: true
      } as ScheduleCallResponse),
      { status: 200 }
    );
  } catch (error) {
    console.error('Error scheduling call:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500 }
    );
  }
}

/**
 * Send confirmation email to user
 */
async function sendConfirmationEmail(
  userName: string,
  userEmail: string,
  phoneNumber: string,
  scheduledTime: Date
): Promise<void> {
  const resendApiKey = process.env.RESEND_API_KEY;

  if (!resendApiKey) {
    console.warn('RESEND_API_KEY not configured');
    return;
  }

  const formattedTime = scheduledTime.toLocaleString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  });

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${resendApiKey}`
    },
    body: JSON.stringify({
      from: 'GB Automation <scoping@consulting-co.com>',
      to: userEmail,
      subject: 'Your Scoping Call is Confirmed 📞',
      html: `
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px;">
          <h2>Hi ${userName},</h2>

          <p>Your technical scoping call is confirmed!</p>

          <div style="background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0 0 8px 0;"><strong>📅 Date & Time</strong></p>
            <p style="margin: 0 0 12px 0; font-size: 16px; font-weight: 600;">${formattedTime}</p>

            <p style="margin: 0 0 8px 0;"><strong>📱 Call Number</strong></p>
            <p style="margin: 0; font-size: 16px; font-weight: 600;">${phoneNumber}</p>
          </div>

          <h3 style="margin: 20px 0 10px 0;">What to Expect:</h3>
          <ul style="color: #666; line-height: 1.8;">
            <li>We'll call you at the scheduled time</li>
            <li>The call will take 20-30 minutes</li>
            <li>Our AI agent will ask about your project goals and requirements</li>
            <li>After the call, you'll receive a detailed scoping document</li>
          </ul>

          <h3 style="margin: 20px 0 10px 0;">Before the Call:</h3>
          <ul style="color: #666; line-height: 1.8;">
            <li>✓ Have your project ideas ready to discuss</li>
            <li>✓ Think about your timeline and budget (optional)</li>
            <li>✓ Be in a quiet place where you can talk freely</li>
          </ul>

          <p style="margin-top: 30px; color: #666; font-size: 14px;">
            Questions? Reply to this email or visit <a href="https://consulting-co.com" style="color: #3b82f6;">our website</a>.
          </p>

          <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">

          <p style="color: #999; font-size: 12px; margin: 0;">
            © 2025 GB Automation. All rights reserved.
          </p>
        </div>
      `
    })
  });

  if (!response.ok) {
    throw new Error(`Failed to send email: ${response.statusText}`);
  }
}

/**
 * Notify team of new scheduling
 */
async function notifyTeam(
  userName: string,
  userEmail: string,
  company: string | undefined,
  scheduledTime: Date
): Promise<void> {
  const resendApiKey = process.env.RESEND_API_KEY;

  if (!resendApiKey) {
    return;
  }

  // Get team emails from environment or database
  const teamEmails = process.env.TEAM_EMAIL_LIST?.split(',') || [];

  if (teamEmails.length === 0) {
    return;
  }

  const formattedTime = scheduledTime.toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${resendApiKey}`
    },
    body: JSON.stringify({
      from: 'GB Automation <scoping@consulting-co.com>',
      to: teamEmails,
      subject: `New Scoping Call Scheduled: ${userName}`,
      html: `
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
          <h2>New Scoping Call Scheduled</h2>

          <p><strong>${userName}</strong> has scheduled a scoping call.</p>

          <div style="background: #f3f4f6; padding: 12px; border-radius: 4px; margin: 12px 0;">
            <p><strong>Name:</strong> ${userName}</p>
            <p><strong>Email:</strong> ${userEmail}</p>
            ${company ? `<p><strong>Company:</strong> ${company}</p>` : ''}
            <p><strong>Scheduled:</strong> ${formattedTime}</p>
          </div>

          <p>After the call completes, you'll be able to review the discovery in the dashboard.</p>

          <p><a href="https://your-domain.com/dashboard" style="background: #3b82f6; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: inline-block;">View Dashboard</a></p>
        </div>
      `
    })
  });
}

/**
 * GET /api/schedule-call/available-slots
 * Get available time slots for next 14 days
 */
export async function GET(request: Request): Promise<Response> {
  try {
    const url = new URL(request.url);
    const timezone = url.searchParams.get('timezone') || 'America/New_York';

    const slots = generateAvailableSlots(timezone);

    return new Response(JSON.stringify({ slots }), { status: 200 });
  } catch (error) {
    console.error('Error getting available slots:', error);
    return new Response(
      JSON.stringify({ error: 'Failed to get available slots' }),
      { status: 500 }
    );
  }
}

/**
 * Generate available time slots
 */
function generateAvailableSlots(timezone: string): string[] {
  const slots: string[] = [];
  const now = new Date();

  // Generate slots for next 14 days
  for (let dayOffset = 1; dayOffset <= 14; dayOffset++) {
    const date = new Date(now);
    date.setDate(date.getDate() + dayOffset);

    // Skip weekends
    if (date.getDay() === 0 || date.getDay() === 6) {
      continue;
    }

    // Add time slots: 9am, 10am, 2pm, 3pm, 4pm
    const times = [9, 10, 14, 15, 16];

    for (const hour of times) {
      date.setHours(hour, 0, 0, 0);
      slots.push(date.toISOString());
    }
  }

  return slots;
}
