"""
HTML Template Generator for Study Plans.
Creates beautiful, responsive HTML output from study plan data.
"""
from typing import Dict, List, Any
from datetime import datetime


def generate_plan_html(plan_data: Dict[str, Any]) -> str:
    """
    Generate a complete HTML document from study plan data.
    
    Args:
        plan_data: The parsed study plan data
        
    Returns:
        Complete HTML string ready for rendering
    """
    title = plan_data.get("title", "Kế hoạch học tập")
    summary = plan_data.get("summary", "")
    subjects = plan_data.get("subjects", [])
    daily_schedules = plan_data.get("dailySchedules", [])
    milestones = plan_data.get("milestones", [])
    tips = plan_data.get("tips", [])
    start_date = plan_data.get("startDate", "")
    end_date = plan_data.get("endDate", "")
    weekly_hours = plan_data.get("weeklyHours", 0)
    
    # Generate subject cards
    subjects_html = _generate_subjects_section(subjects)
    
    # Generate schedule table
    schedule_html = _generate_schedule_section(daily_schedules)
    
    # Generate milestones timeline
    milestones_html = _generate_milestones_section(milestones)
    
    # Generate tips list
    tips_html = _generate_tips_section(tips)
    
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary: #6366f1;
            --primary-light: #818cf8;
            --secondary: #f59e0b;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1f2937;
            --light: #f3f4f6;
            --white: #ffffff;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: var(--dark);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: var(--white);
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: var(--white);
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        header .meta {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        header .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
        }}
        
        .summary {{
            background: var(--light);
            padding: 30px 40px;
            font-size: 1.1rem;
            border-left: 4px solid var(--primary);
            margin: 30px;
            border-radius: 0 10px 10px 0;
        }}
        
        main {{
            padding: 30px 40px;
        }}
        
        section {{
            margin-bottom: 40px;
        }}
        
        section h2 {{
            font-size: 1.5rem;
            color: var(--primary);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        section h2::before {{
            content: '';
            width: 4px;
            height: 24px;
            background: var(--primary);
            border-radius: 2px;
        }}
        
        /* Subject Cards */
        .subjects-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .subject-card {{
            background: var(--white);
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .subject-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        }}
        
        .subject-card h3 {{
            font-size: 1.2rem;
            margin-bottom: 10px;
            color: var(--dark);
        }}
        
        .subject-card .priority {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .priority-high {{ background: #fee2e2; color: var(--danger); }}
        .priority-medium {{ background: #fef3c7; color: var(--warning); }}
        .priority-low {{ background: #d1fae5; color: var(--success); }}
        
        .subject-card .hours {{
            color: #6b7280;
            font-size: 0.9rem;
            margin: 10px 0;
        }}
        
        .topics-list {{
            list-style: none;
            margin-top: 15px;
        }}
        
        .topics-list li {{
            padding: 6px 0;
            padding-left: 20px;
            position: relative;
            font-size: 0.9rem;
            color: #4b5563;
        }}
        
        .topics-list li::before {{
            content: '→';
            position: absolute;
            left: 0;
            color: var(--primary);
        }}
        
        /* Schedule Table */
        .schedule-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        .schedule-table th {{
            background: var(--primary);
            color: var(--white);
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .schedule-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .schedule-table tr:hover {{
            background: var(--light);
        }}
        
        .schedule-table .time {{
            font-family: 'Courier New', monospace;
            color: var(--primary);
            font-weight: 600;
        }}
        
        .activity-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        .activity-study {{ background: #dbeafe; color: #1e40af; }}
        .activity-review {{ background: #e0e7ff; color: #3730a3; }}
        .activity-practice {{ background: #d1fae5; color: #065f46; }}
        .activity-break {{ background: #fef3c7; color: #92400e; }}
        
        /* Milestones Timeline */
        .timeline {{
            position: relative;
            padding-left: 30px;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 8px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: var(--primary-light);
        }}
        
        .milestone {{
            position: relative;
            margin-bottom: 25px;
            padding: 15px 20px;
            background: var(--light);
            border-radius: 10px;
        }}
        
        .milestone::before {{
            content: '';
            position: absolute;
            left: -26px;
            top: 20px;
            width: 12px;
            height: 12px;
            background: var(--primary);
            border-radius: 50%;
            border: 3px solid var(--white);
            box-shadow: 0 0 0 3px var(--primary-light);
        }}
        
        .milestone .date {{
            font-size: 0.85rem;
            color: var(--primary);
            font-weight: 600;
            margin-bottom: 5px;
        }}
        
        .milestone h4 {{
            font-size: 1.1rem;
            margin-bottom: 8px;
        }}
        
        .milestone p {{
            color: #4b5563;
            font-size: 0.95rem;
        }}
        
        /* Tips Section */
        .tips-list {{
            display: grid;
            gap: 15px;
        }}
        
        .tip-item {{
            display: flex;
            align-items: flex-start;
            gap: 15px;
            padding: 15px 20px;
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-radius: 10px;
        }}
        
        .tip-icon {{
            font-size: 1.5rem;
            flex-shrink: 0;
        }}
        
        .tip-text {{
            color: #92400e;
            font-size: 0.95rem;
        }}
        
        footer {{
            background: var(--dark);
            color: var(--light);
            padding: 20px 40px;
            text-align: center;
            font-size: 0.9rem;
        }}
        
        footer a {{
            color: var(--primary-light);
            text-decoration: none;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            header {{
                padding: 25px 20px;
            }}
            
            header h1 {{
                font-size: 1.8rem;
            }}
            
            main {{
                padding: 20px;
            }}
            
            .subjects-grid {{
                grid-template-columns: 1fr;
            }}
            
            .schedule-table {{
                font-size: 0.85rem;
            }}
            
            .schedule-table th,
            .schedule-table td {{
                padding: 10px;
            }}
        }}
        
        /* Print styles */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
            
            header {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 {title}</h1>
            <div class="meta">
                <div class="meta-item">
                    📅 <span>{start_date} → {end_date}</span>
                </div>
                <div class="meta-item">
                    ⏰ <span>{weekly_hours} giờ/tuần</span>
                </div>
                <div class="meta-item">
                    📖 <span>{len(subjects)} môn học</span>
                </div>
            </div>
        </header>
        
        <div class="summary">
            {summary}
        </div>
        
        <main>
            {subjects_html}
            {schedule_html}
            {milestones_html}
            {tips_html}
        </main>
        
        <footer>
            <p>Được tạo bởi <a href="#">Student Study Planner</a> • {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </footer>
    </div>
</body>
</html>"""


def _generate_subjects_section(subjects: List[Dict]) -> str:
    """Generate the subjects section HTML."""
    if not subjects:
        return ""
    
    cards = []
    for subject in subjects:
        name = subject.get("name", "")
        priority = subject.get("priority", "medium")
        total_hours = subject.get("totalHours", 0)
        topics = subject.get("topics", [])
        
        topics_html = "".join(f"<li>{topic}</li>" for topic in topics[:5])
        if len(topics) > 5:
            topics_html += f"<li>... và {len(topics) - 5} chủ đề khác</li>"
        
        cards.append(f"""
            <div class="subject-card">
                <h3>{name}</h3>
                <span class="priority priority-{priority}">{priority}</span>
                <p class="hours">⏱️ {total_hours} giờ học</p>
                <ul class="topics-list">
                    {topics_html}
                </ul>
            </div>
        """)
    
    return f"""
        <section>
            <h2>Môn học</h2>
            <div class="subjects-grid">
                {"".join(cards)}
            </div>
        </section>
    """


def _generate_schedule_section(daily_schedules: List[Dict]) -> str:
    """Generate the schedule section HTML."""
    if not daily_schedules:
        return ""
    
    rows = []
    for day in daily_schedules[:7]:  # Show first week
        date = day.get("date", "")
        day_of_week = day.get("dayOfWeek", "")
        sessions = day.get("sessions", [])
        
        for session in sessions:
            start_time = session.get("startTime", "")
            end_time = session.get("endTime", "")
            subject = session.get("subject", "")
            topic = session.get("topic", "")
            activity_type = session.get("activityType", "study")
            
            rows.append(f"""
                <tr>
                    <td>{date}<br><small>{day_of_week}</small></td>
                    <td class="time">{start_time} - {end_time}</td>
                    <td>{subject}</td>
                    <td>{topic}</td>
                    <td><span class="activity-badge activity-{activity_type}">{activity_type}</span></td>
                </tr>
            """)
    
    return f"""
        <section>
            <h2>Lịch học chi tiết</h2>
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Ngày</th>
                        <th>Thời gian</th>
                        <th>Môn</th>
                        <th>Nội dung</th>
                        <th>Loại</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
            {f'<p style="margin-top: 15px; color: #6b7280;">Hiển thị 7 ngày đầu tiên. Kế hoạch đầy đủ có {len(daily_schedules)} ngày.</p>' if len(daily_schedules) > 7 else ''}
        </section>
    """


def _generate_milestones_section(milestones: List[Dict]) -> str:
    """Generate the milestones timeline HTML."""
    if not milestones:
        return ""
    
    items = []
    for milestone in milestones:
        date = milestone.get("date", "")
        title = milestone.get("title", "")
        description = milestone.get("description", "")
        
        items.append(f"""
            <div class="milestone">
                <div class="date">📌 {date}</div>
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
        """)
    
    return f"""
        <section>
            <h2>Các mốc quan trọng</h2>
            <div class="timeline">
                {"".join(items)}
            </div>
        </section>
    """


def _generate_tips_section(tips: List[str]) -> str:
    """Generate the tips section HTML."""
    if not tips:
        return ""
    
    icons = ["💡", "🎯", "📝", "🧠", "⚡", "🌟", "🔑", "✨"]
    items = []
    
    for i, tip in enumerate(tips):
        icon = icons[i % len(icons)]
        items.append(f"""
            <div class="tip-item">
                <span class="tip-icon">{icon}</span>
                <span class="tip-text">{tip}</span>
            </div>
        """)
    
    return f"""
        <section>
            <h2>Lời khuyên</h2>
            <div class="tips-list">
                {"".join(items)}
            </div>
        </section>
    """
