import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Template, Environment, FileSystemLoader

class HTMLReporter:
    """Generate HTML reports for validation results"""
    
    def __init__(self, output_dir: str = "reports", template_dir: str = "templates"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = Path(template_dir)
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def generate_report(self, results: List[Dict[str, Any]], summary: Dict[str, Any], 
                       spec_info: Dict[str, Any]) -> str:
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"api_validation_report_{timestamp}.html"
        report_path = self.output_dir / report_filename
        
        # Prepare data for template
        template_data = {
            'title': 'API Validation Report',
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'spec_info': spec_info,
            'summary': summary,
            'results': results,
            'failed_results': [r for r in results if not r['success']],
            'passed_results': [r for r in results if r['success']]
        }
        
        # Generate HTML
        html_content = self._render_template(template_data)
        
        # Write to file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _render_template(self, data: Dict[str, Any]) -> str:
        # Load and render the HTML template from file
        for file_name in ["report_template.html", "scripts.js", "styles.css"]:
            if not (self.template_dir / file_name).exists():
                raise FileNotFoundError(f"Template file '{file_name}' not found in '{self.template_dir}'")
        template = self.env.get_template('report_template.html')
        return template.render(**data)

class JSONReporter:
    """Generate JSON reports for validation results"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, results: List[Dict[str, Any]], summary: Dict[str, Any], 
                       spec_info: Dict[str, Any]) -> str:
        # Generate JSON report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"api_validation_report_{timestamp}.json"
        report_path = self.output_dir / report_filename
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'spec_info': spec_info,
            'summary': summary,
            'results': results
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return str(report_path)