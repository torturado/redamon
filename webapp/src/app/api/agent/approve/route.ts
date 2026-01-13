import { NextRequest, NextResponse } from 'next/server'
import type { ApprovalRequest, QueryResponse } from '../route'

const AGENT_API_BASE_URL = process.env.AGENT_API_URL || process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8080'

export async function POST(request: NextRequest) {
  try {
    const body: ApprovalRequest = await request.json()

    if (!body.session_id || !body.user_id || !body.project_id || !body.decision) {
      return NextResponse.json(
        { error: 'session_id, user_id, project_id, and decision are required' },
        { status: 400 }
      )
    }

    if (!['approve', 'modify', 'abort'].includes(body.decision)) {
      return NextResponse.json(
        { error: 'decision must be one of: approve, modify, abort' },
        { status: 400 }
      )
    }

    const response = await fetch(`${AGENT_API_BASE_URL}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorText = await response.text()
      return NextResponse.json(
        { error: `Agent API error: ${response.status} - ${errorText}` },
        { status: response.status }
      )
    }

    const data: QueryResponse = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Agent approval error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Approval failed' },
      { status: 500 }
    )
  }
}
