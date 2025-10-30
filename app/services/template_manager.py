"""Template management service for storing message templates"""
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from app.utils.file_utils import (
    get_data_path, ensure_dir_exists, 
    load_yaml, save_yaml, read_text_file, write_text_file
)
from app.utils.datetime_utils import get_est_now, format_datetime_for_filename, format_for_display


class TemplateManager:
    """Manages message templates for outreach"""
    
    def __init__(self):
        self.templates_dir = get_data_path('templates')
        ensure_dir_exists(self.templates_dir)
        self.templates_meta_path = self.templates_dir / 'templates_meta.yaml'
    
    def create_template(
        self,
        title: str,
        delivery_method: str,
        content: str
    ) -> Dict:
        """Create a new template"""
        template_id = format_datetime_for_filename(get_est_now())
        
        # Create template metadata
        now = get_est_now()
        template_data = {
            'id': template_id,
            'title': title,
            'delivery_method': delivery_method,
            'created_at': now.isoformat(),
            'created_at_display': format_for_display(now),
            'content_file': f'{template_id}.html'
        }
        
        # Save content as HTML (rich text)
        content_path = self.templates_dir / template_data['content_file']
        write_text_file(content, content_path)
        
        # Load existing templates metadata
        templates = self._load_templates_meta()
        templates.append(template_data)
        
        # Save updated metadata
        self._save_templates_meta(templates)
        
        return template_data
    
    def list_templates(self) -> List[Dict]:
        """List all templates"""
        templates = self._load_templates_meta()
        
        # Load content for each template and ensure display timestamp is set
        for template in templates:
            content_path = self.templates_dir / template['content_file']
            if content_path.exists():
                template['content'] = read_text_file(content_path)
            else:
                template['content'] = ''
            
            # Ensure created_at_display is set (reformat if needed)
            if 'created_at_display' not in template or not template['created_at_display']:
                try:
                    from datetime import datetime
                    from app.utils.datetime_utils import format_for_display
                    if 'created_at' in template:
                        dt = datetime.fromisoformat(template['created_at'])
                        template['created_at_display'] = format_for_display(dt)
                except:
                    template['created_at_display'] = template.get('created_at', 'Date not available')
        
        # Sort by created_at descending (newest first)
        templates.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return templates
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get a specific template by ID"""
        templates = self._load_templates_meta()
        
        for template in templates:
            if template['id'] == template_id:
                # Load content
                content_path = self.templates_dir / template['content_file']
                if content_path.exists():
                    template['content'] = read_text_file(content_path)
                else:
                    template['content'] = ''
                
                # Ensure created_at_display is set
                if 'created_at_display' not in template or not template['created_at_display']:
                    try:
                        from datetime import datetime
                        from app.utils.datetime_utils import format_for_display
                        if 'created_at' in template:
                            dt = datetime.fromisoformat(template['created_at'])
                            template['created_at_display'] = format_for_display(dt)
                    except:
                        template['created_at_display'] = template.get('created_at', 'Date not available')
                
                return template
        
        return None
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        templates = self._load_templates_meta()
        
        template_to_delete = None
        for template in templates:
            if template['id'] == template_id:
                template_to_delete = template
                break
        
        if template_to_delete:
            # Delete content file
            content_path = self.templates_dir / template_to_delete['content_file']
            if content_path.exists():
                content_path.unlink()
            
            # Remove from metadata
            templates.remove(template_to_delete)
            self._save_templates_meta(templates)
            return True
        
        return False
    
    def _load_templates_meta(self) -> List[Dict]:
        """Load templates metadata"""
        if not self.templates_meta_path.exists():
            return []
        
        data = load_yaml(self.templates_meta_path)
        return data.get('templates', [])
    
    def _save_templates_meta(self, templates: List[Dict]) -> None:
        """Save templates metadata"""
        data = {'templates': templates}
        save_yaml(data, self.templates_meta_path)

