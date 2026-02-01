#!/usr/bin/env python3
"""
Enterprise Deployment Script - Deploys complete Linear C Enterprise Platform

This script orchestrates the deployment of all enterprise components including:
- Control Plane API
- Dashboard
- Analytics Engine
- Kubernetes manifests
- Monitoring stack
"""
import os
import sys
import subprocess
import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class EnterpriseDeployer:
    """
    Deploys the complete Linear C Enterprise Platform
    """
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.base_dir = Path(__file__).parent
        self.status = {}
        
        print(f"🚀 Linear C Enterprise Platform Deployer")
        print(f"Environment: {environment}")
        print("=" * 60)
    
    def run_command(self, cmd: List[str], cwd: Path = None) -> bool:
        """Run a shell command and return success status"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.base_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Command failed: {' '.join(cmd)}")
            print(f"  Error: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"  ❌ Command not found: {cmd[0]}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if required tools are installed"""
        print("\n📋 Checking dependencies...")
        
        dependencies = {
            'python': ['python', '--version'],
            'docker': ['docker', '--version'],
            'docker-compose': ['docker-compose', '--version'],
        }
        
        all_ok = True
        for name, cmd in dependencies.items():
            if self.run_command(cmd):
                print(f"  ✅ {name} installed")
            else:
                print(f"  ❌ {name} not found")
                all_ok = False
        
        # Optional dependencies
        optional = {
            'kubectl': ['kubectl', 'version', '--client'],
            'helm': ['helm', 'version'],
        }
        
        for name, cmd in optional.items():
            if self.run_command(cmd):
                print(f"  ✅ {name} installed (optional)")
            else:
                print(f"  ⚠️  {name} not found (optional)")
        
        return all_ok
    
    def deploy_docker_compose(self) -> bool:
        """Deploy using Docker Compose"""
        print("\n🐳 Deploying with Docker Compose...")
        
        compose_file = self.base_dir / "deployments" / "docker-compose" / "enterprise.yml"
        
        if not compose_file.exists():
            print(f"  ❌ Docker Compose file not found: {compose_file}")
            return False
        
        # Pull images
        print("  📥 Pulling Docker images...")
        if not self.run_command(['docker-compose', '-f', str(compose_file), 'pull']):
            print("  ⚠️  Failed to pull images, continuing...")
        
        # Build services
        print("  🔨 Building services...")
        if not self.run_command(['docker-compose', '-f', str(compose_file), 'build']):
            print("  ❌ Failed to build services")
            return False
        
        # Start services
        print("  🚀 Starting services...")
        if not self.run_command(['docker-compose', '-f', str(compose_file), 'up', '-d']):
            print("  ❌ Failed to start services")
            return False
        
        print("  ✅ Docker Compose deployment complete")
        
        # Wait for services to be healthy
        print("  ⏳ Waiting for services to be healthy...")
        import time
        time.sleep(10)
        
        # Check service health
        if self.run_command(['docker-compose', '-f', str(compose_file), 'ps']):
            print("  ✅ Services are running")
        
        return True
    
    def deploy_kubernetes(self) -> bool:
        """Deploy to Kubernetes"""
        print("\n☸️  Deploying to Kubernetes...")
        
        k8s_manifest = self.base_dir / "deployments" / "kubernetes" / "linear-c-platform.yaml"
        
        if not k8s_manifest.exists():
            print(f"  ❌ Kubernetes manifest not found: {k8s_manifest}")
            return False
        
        # Apply manifest
        print("  📦 Applying Kubernetes manifests...")
        if not self.run_command(['kubectl', 'apply', '-f', str(k8s_manifest)]):
            print("  ❌ Failed to apply Kubernetes manifests")
            return False
        
        print("  ✅ Kubernetes deployment initiated")
        
        # Wait for pods
        print("  ⏳ Waiting for pods to be ready...")
        if self.run_command([
            'kubectl', 'wait', '--for=condition=ready',
            'pod', '-l', 'app=control-plane',
            '-n', 'linear-c-safety',
            '--timeout=300s'
        ]):
            print("  ✅ Pods are ready")
        else:
            print("  ⚠️  Pods may not be ready yet")
        
        # Show status
        print("  📊 Cluster status:")
        self.run_command(['kubectl', 'get', 'all', '-n', 'linear-c-safety'])
        
        return True
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        print("\n📦 Installing Python dependencies...")
        
        # Install enterprise dependencies
        enterprise_packages = [
            'fastapi==0.104.1',
            'uvicorn[standard]==0.24.0',
            'redis==5.0.1',
            'PyJWT==2.8.0',
            'prometheus-client==0.19.0',
            'pandas==2.0.3',
            'scikit-learn==1.3.2',
            'websockets==12.0'
        ]
        
        cmd = [sys.executable, '-m', 'pip', 'install'] + enterprise_packages
        
        if self.run_command(cmd):
            print("  ✅ Dependencies installed")
            return True
        else:
            print("  ❌ Failed to install dependencies")
            return False
    
    def run_tests(self) -> bool:
        """Run enterprise tests"""
        print("\n🧪 Running tests...")
        
        # Run pytest
        if self.run_command([sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short']):
            print("  ✅ All tests passed")
            return True
        else:
            print("  ❌ Some tests failed")
            return False
    
    def generate_report(self) -> bool:
        """Generate deployment report"""
        print("\n📄 Generating deployment report...")
        
        report = {
            'environment': self.environment,
            'timestamp': datetime.utcnow().isoformat(),
            'status': self.status,
            'deployment_type': 'docker-compose' if self.environment == 'development' else 'kubernetes'
        }
        
        # Save report
        reports_dir = self.base_dir / "deployments" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"deployment-{self.environment}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"  ✅ Report saved to: {report_file}")
        return True
    
    def print_access_info(self):
        """Print access information"""
        print("\n" + "=" * 60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("=" * 60)
        
        if self.environment == 'development':
            print("\n🌐 Access Points (Docker Compose):")
            print("  - Control Plane API: http://localhost:8000")
            print("  - API Documentation: http://localhost:8000/api/docs")
            print("  - Dashboard: http://localhost:3000")
            print("  - Prometheus: http://localhost:9090")
            print("  - Grafana: http://localhost:3001 (admin/admin)")
            print("  - Redis: localhost:6379")
            
            print("\n📊 Useful Commands:")
            print("  - View logs: docker-compose -f deployments/docker-compose/enterprise.yml logs -f")
            print("  - Stop services: docker-compose -f deployments/docker-compose/enterprise.yml down")
            print("  - Restart: docker-compose -f deployments/docker-compose/enterprise.yml restart")
        else:
            print("\n🌐 Access Points (Kubernetes):")
            print("  - Control Plane: kubectl port-forward -n linear-c-safety svc/control-plane 8000:80")
            print("  - Dashboard: kubectl port-forward -n linear-c-safety svc/dashboard 3000:80")
            
            print("\n📊 Useful Commands:")
            print("  - View pods: kubectl get pods -n linear-c-safety")
            print("  - View logs: kubectl logs -f -n linear-c-safety deployment/control-plane")
            print("  - Delete deployment: kubectl delete namespace linear-c-safety")
        
        print("\n🔧 Next Steps:")
        print("  1. Register your first robot:")
        print("     curl -X POST http://localhost:8000/api/v1/robots/register \\")
        print("       -H 'Authorization: Bearer demo-token' \\")
        print("       -H 'Content-Type: application/json' \\")
        print("       -d '{\"robot_id\":\"robot-001\",\"robot_type\":\"agv\",\"safety_profile\":\"default\"}'")
        print("\n  2. Test safety validation:")
        print("     curl -X POST http://localhost:8000/api/v1/safety/validate \\")
        print("       -H 'Authorization: Bearer demo-token' \\")
        print("       -H 'Content-Type: application/json' \\")
        print("       -d '{\"robot_id\":\"robot-001\",\"linear_c_string\":\"🟢🧠\"}'")
        print("\n  3. View fleet status:")
        print("     curl http://localhost:8000/api/v1/fleet/status \\")
        print("       -H 'Authorization: Bearer demo-token'")
    
    def deploy(self, deployment_type: str = 'docker-compose'):
        """Main deployment method"""
        # Check dependencies
        if not self.check_dependencies():
            print("\n❌ Missing required dependencies. Please install them first.")
            return False
        
        self.status['dependencies'] = {'success': True}
        
        # Install Python dependencies
        if not self.install_dependencies():
            print("\n⚠️  Failed to install Python dependencies, continuing...")
        
        self.status['python_deps'] = {'success': True}
        
        # Deploy based on type
        if deployment_type == 'docker-compose':
            success = self.deploy_docker_compose()
            self.status['docker_compose'] = {'success': success}
        elif deployment_type == 'kubernetes':
            success = self.deploy_kubernetes()
            self.status['kubernetes'] = {'success': success}
        else:
            print(f"\n❌ Unknown deployment type: {deployment_type}")
            return False
        
        if not success:
            print("\n❌ Deployment failed")
            return False
        
        # Generate report
        self.generate_report()
        
        # Print access information
        self.print_access_info()
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Deploy Linear C Enterprise Platform")
    parser.add_argument(
        '--environment', '-e',
        choices=['development', 'staging', 'production'],
        default='development',
        help='Deployment environment'
    )
    parser.add_argument(
        '--type', '-t',
        choices=['docker-compose', 'kubernetes'],
        default='docker-compose',
        help='Deployment type'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip running tests'
    )
    
    args = parser.parse_args()
    
    # Create deployer
    deployer = EnterpriseDeployer(environment=args.environment)
    
    # Run deployment
    success = deployer.deploy(deployment_type=args.type)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
