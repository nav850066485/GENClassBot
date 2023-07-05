from flask_admin.contrib.sqla import ModelView
from Packages import db
from Packages.models import Mentor,Mentee
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask import flash

class UserAdminView(ModelView):

    @action('assign_role', 'Assign as Mentor', 'Are you sure you want to assign this user as Mentor?')
    def action_assign_role(self, ids):
        for id in ids:
            user = self.get_one(id)
            if user.role != 'Mentor':
                mentor = Mentor(name=user.username,user=user)
                db.session.add(mentor)

                # Delete the user from the Mentee table
                mentee = Mentee.query.filter_by(user_id=user.id).first()
                if mentee:
                    db.session.delete(mentee)

                user.role = 'Mentor'  # Assigning user as Mentor
                flash(f'{user.username} has been assigned as a Mentor', 'success')
            else:
                flash(f'{user.username} is already a Mentor', 'info')
        self.session.commit()

