import os
import logging
import uuid
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, jsonify, send_file, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Media, DetectionResult, Report, SecurityLog
from forms import RegistrationForm, LoginForm, UploadMediaForm, EditUserForm
from deepfake_detector import detect_deepfake, generate_heatmap
from utils import generate_report, get_file_extension, is_video


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        # Make the first user an admin
        if User.query.count() == 0:
            user.is_admin = True
            
        db.session.add(user)
        db.session.commit()
        
        # Log the registration
        log = SecurityLog(
            event_type='REGISTRATION',
            event_info=f'User {user.username} registered',
            ip_address=request.remote_addr,
            user_id=user.id
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            
            # Log the login
            log = SecurityLog(
                event_type='LOGIN',
                event_info=f'User {user.username} logged in',
                ip_address=request.remote_addr,
                user_id=user.id
            )
            db.session.add(log)
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    # Log the logout
    log = SecurityLog(
        event_type='LOGOUT',
        event_info=f'User {current_user.username} logged out',
        ip_address=request.remote_addr,
        user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    recent_results = DetectionResult.query.filter_by(user_id=current_user.id).order_by(DetectionResult.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', recent_results=recent_results)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadMediaForm()
    
    if form.validate_on_submit():
        file = form.media.data
        original_filename = secure_filename(file.filename)
        
        # Create unique filename
        file_extension = get_file_extension(original_filename)
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create upload folder if it doesn't exist
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Determine if it's an image or video
        media_type = 'video' if is_video(file_extension) else 'image'
        
        # Create media record
        media = Media(
            filename=unique_filename,
            original_filename=original_filename,
            media_type=media_type,
            processed=False
        )
        db.session.add(media)
        db.session.commit()
        
        # Process the media (detect deepfake)
        result, confidence = detect_deepfake(file_path, media_type)
        
        # Generate heatmap
        heatmap_filename = f"heatmap_{unique_filename}"
        heatmap_path = os.path.join(upload_folder, heatmap_filename)
        generate_heatmap(file_path, heatmap_path, result)
        
        # Create detection result
        detection_result = DetectionResult(
            user_id=current_user.id,
            media_id=media.id,
            is_deepfake=result,
            confidence_score=confidence,
            heatmap_path=heatmap_filename
        )
        db.session.add(detection_result)
        
        # Update media as processed
        media.processed = True
        db.session.commit()
        
        # Log the detection
        log = SecurityLog(
            event_type='DETECTION',
            event_info=f'User {current_user.username} performed deepfake detection on {original_filename}',
            ip_address=request.remote_addr,
            user_id=current_user.id
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Media uploaded and processed successfully!', 'success')
        return redirect(url_for('results', result_id=detection_result.id))
    
    return render_template('upload.html', form=form)


@app.route('/results/<int:result_id>')
@login_required
def results(result_id):
    result = DetectionResult.query.get_or_404(result_id)
    
    # Check if the result belongs to the current user
    if result.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this result.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('results.html', result=result)


@app.route('/generate_report/<int:result_id>')
@login_required
def generate_report_route(result_id):
    result = DetectionResult.query.get_or_404(result_id)
    
    # Check if the result belongs to the current user
    if result.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to generate this report.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Generate report
    report_filename = f"report_{uuid.uuid4().hex}.pdf"
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
    
    generate_report(result, report_path)
    
    # Create report record
    report = Report(
        user_id=current_user.id,
        detection_result_id=result.id,
        report_path=report_filename
    )
    db.session.add(report)
    db.session.commit()
    
    # Log the report generation
    log = SecurityLog(
        event_type='REPORT',
        event_info=f'User {current_user.username} generated a report for detection {result.id}',
        ip_address=request.remote_addr,
        user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Report generated successfully!', 'success')
    return redirect(url_for('results', result_id=result.id))


@app.route('/download_report/<int:report_id>')
@login_required
def download_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if the report belongs to the current user
    if report.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to download this report.', 'danger')
        return redirect(url_for('dashboard'))
    
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], report.report_path)
    return send_file(report_path, as_attachment=True)


@app.route('/history')
@login_required
def history():
    results = DetectionResult.query.filter_by(user_id=current_user.id).order_by(DetectionResult.created_at.desc()).all()
    return render_template('history.html', results=results)


@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin dashboard.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    logs = SecurityLog.query.order_by(SecurityLog.timestamp.desc()).limit(100).all()
    
    return render_template('admin_dashboard.html', users=users, logs=logs)


@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to edit users.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent editing own admin status
    if user.id == current_user.id:
        flash('You cannot modify your own admin status.', 'warning')
        return redirect(url_for('admin_dashboard'))
        
    form = EditUserForm(user.username, user.email)
    
    if form.validate_on_submit():
        old_username = user.username
        user.username = form.username.data
        user.email = form.email.data
        
        # Only allow changing admin status if not editing self
        if user.id != current_user.id:
            user.is_admin = form.is_admin.data
        
        # Update password if provided
        if form.new_password.data:
            user.set_password(form.new_password.data)
        
        try:
            db.session.commit()
            
            # Log the user edit
            changes = []
            if old_username != user.username:
                changes.append(f"username changed to {user.username}")
            if form.new_password.data:
                changes.append("password updated")
            if user.id != current_user.id and user.is_admin != form.is_admin.data:
                changes.append(f"admin status changed to {user.is_admin}")
                
            log = SecurityLog(
                event_type='USER_EDIT',
                event_info=f'Admin {current_user.username} edited user {user.username} ({", ".join(changes)})',
                ip_address=request.remote_addr,
                user_id=current_user.id
            )
            db.session.add(log)
            db.session.commit()
            
            flash(f'User {user.username} has been updated successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the user.', 'danger')
            app.logger.error(f'Error updating user: {str(e)}')
    
    # Pre-populate form with user data
    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.is_admin.data = user.is_admin
    
    return render_template('edit_user.html', form=form, user=user)


@app.route('/admin/user/<int:user_id>/delete')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to delete users.', 'danger')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Prevent deleting the last admin
    admin_count = User.query.filter_by(is_admin=True).count()
    if user.is_admin and admin_count <= 1:
        flash('Cannot delete the last admin user.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        # Store username and info for the log
        username = user.username
        user_info = f"User had {len(user.detection_results)} detection results and {len(user.reports)} reports"
        
        # Delete user's uploaded files
        for result in user.detection_results:
            if result.media:
                # Delete original media file
                media_path = os.path.join(app.config['UPLOAD_FOLDER'], result.media.filename)
                if os.path.exists(media_path):
                    os.remove(media_path)
                # Delete heatmap if exists
                if result.heatmap_path:
                    heatmap_path = os.path.join(app.config['UPLOAD_FOLDER'], result.heatmap_path)
                    if os.path.exists(heatmap_path):
                        os.remove(heatmap_path)
        
        # Delete user (this will cascade delete their results, reports, etc.)
        db.session.delete(user)
        db.session.commit()
        
        # Log the user deletion with additional info
        log = SecurityLog(
            event_type='USER_DELETE',
            event_info=f'Admin {current_user.username} deleted user {username}. {user_info}',
            ip_address=request.remote_addr,
            user_id=current_user.id
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'User {username} and all associated data have been deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the user.', 'danger')
        app.logger.error(f'Error deleting user: {str(e)}')
        
    return redirect(url_for('admin_dashboard'))
