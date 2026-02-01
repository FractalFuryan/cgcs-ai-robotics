"""
Linear C Safety Certification Authority
Certifies robots, operators, and organizations for safety compliance
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid


class CertificationLevel(Enum):
    """Safety certification levels"""
    BASIC = "basic"           # Passes basic safety tests
    STANDARD = "standard"     # Meets industry standards
    ADVANCED = "advanced"     # Exceeds standards with advanced features
    PREMIUM = "premium"       # Highest safety certification
    CUSTOM = "custom"         # Custom certification for specific use cases


class CertificationType(Enum):
    """Types of certifications"""
    ROBOT_MODEL = "robot_model"       # Certification for specific robot model
    ROBOT_FLEET = "robot_fleet"       # Certification for entire fleet
    OPERATOR = "operator"             # Human operator certification
    ORGANIZATION = "organization"     # Organization safety certification
    FACILITY = "facility"             # Facility/workspace certification
    SOFTWARE = "software"             # Safety software certification


@dataclass
class SafetyRequirement:
    """Individual safety requirement"""
    id: str
    description: str
    linear_c_pattern: Optional[str]  # Required Linear C pattern
    test_procedure: str              # How to test this requirement
    passing_criteria: str            # Criteria for passing
    weight: float                    # Weight in overall score (0-1)
    mandatory: bool                  # Must pass to get certification


@dataclass
class CertificationStandard:
    """Safety certification standard"""
    id: str
    name: str
    version: str
    description: str
    requirements: List[SafetyRequirement]
    min_score: float                 # Minimum overall score to pass (0-100)
    validity_days: int               # How long certification is valid
    required_for: List[str]          # What this is required for (industries, etc.)
    based_on: List[str]              # Standards this is based on (ISO, etc.)


@dataclass
class CertificationResult:
    """Result of a certification test"""
    requirement_id: str
    passed: bool
    score: float                     # 0-100
    evidence: Dict                   # Test evidence (logs, videos, data)
    notes: str
    timestamp: datetime


@dataclass
class Certificate:
    """Issued safety certificate"""
    certificate_id: str
    type: CertificationType
    level: CertificationLevel
    standard: CertificationStandard
    certified_entity: str            # ID of robot/operator/organization
    issuer: str                      # Certification authority
    issue_date: datetime
    expiry_date: datetime
    overall_score: float             # 0-100
    requirement_results: List[CertificationResult]
    blockchain_hash: Optional[str] = None  # Immutable proof on blockchain
    revocation_reason: Optional[str] = None  # If revoked
    revoked_date: Optional[datetime] = None


class SafetyCertificationAuthority:
    """
    Issues and manages safety certifications
    """
    def __init__(self, authority_name: str = "Linear C Safety Authority"):
        self.authority_name = authority_name
        self.standards = {}
        self.certificates = {}
        self.revoked_certificates = set()
        
        # Load standard certifications
        self._load_standard_certifications()
    
    def create_certification_standard(self, standard: CertificationStandard) -> str:
        """Create a new certification standard"""
        self.standards[standard.id] = standard
        return standard.id
    
    async def certify_robot_model(self, robot_model: str, 
                                manufacturer: str,
                                test_data: Dict) -> Certificate:
        """Certify a specific robot model"""
        # Select appropriate standard based on robot type
        standard = self._select_standard_for_robot(robot_model, test_data)
        
        # Run certification tests
        results = await self._run_certification_tests(standard, test_data)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(standard, results)
        
        # Check if passes minimum score
        if overall_score < standard.min_score:
            raise ValueError(f"Certification failed: Score {overall_score} < minimum {standard.min_score}")
        
        # Determine certification level
        level = self._determine_certification_level(overall_score, standard)
        
        # Create certificate
        certificate = Certificate(
            certificate_id=f"CERT-{uuid.uuid4().hex[:12].upper()}",
            type=CertificationType.ROBOT_MODEL,
            level=level,
            standard=standard,
            certified_entity=robot_model,
            issuer=self.authority_name,
            issue_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=standard.validity_days),
            overall_score=overall_score,
            requirement_results=results,
            blockchain_hash=self._generate_blockchain_hash(robot_model, manufacturer, results)
        )
        
        # Store certificate
        self.certificates[certificate.certificate_id] = certificate
        
        # Publish certification
        await self._publish_certification(certificate)
        
        return certificate
    
    async def certify_operator(self, operator_id: str, 
                             operator_data: Dict,
                             training_certificates: List[str] = None) -> Certificate:
        """Certify a human robot operator"""
        # Check operator training and qualifications
        if not await self._validate_operator_qualifications(operator_id, operator_data, training_certificates):
            raise ValueError("Operator does not meet minimum qualifications")
        
        # Run operator safety tests
        test_results = await self._run_operator_safety_tests(operator_id, operator_data)
        
        # Select operator certification standard
        standard = self.standards.get("operator_standard")
        if not standard:
            standard = self._create_operator_standard()
        
        # Calculate score
        overall_score = self._calculate_operator_score(test_results)
        
        # Create certificate
        certificate = Certificate(
            certificate_id=f"OP-CERT-{uuid.uuid4().hex[:12].upper()}",
            type=CertificationType.OPERATOR,
            level=CertificationLevel.STANDARD if overall_score >= 85 else CertificationLevel.BASIC,
            standard=standard,
            certified_entity=operator_id,
            issuer=self.authority_name,
            issue_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=365),  # 1 year validity
            overall_score=overall_score,
            requirement_results=test_results
        )
        
        self.certificates[certificate.certificate_id] = certificate
        
        return certificate
    
    async def certify_fleet(self, fleet_id: str,
                          fleet_data: Dict,
                          robot_certificates: List[str]) -> Certificate:
        """Certify an entire robot fleet"""
        # Validate all robots in fleet are certified
        if not await self._validate_fleet_certifications(fleet_id, robot_certificates):
            raise ValueError("Not all robots in fleet are properly certified")
        
        # Run fleet-level safety tests
        fleet_results = await self._run_fleet_safety_tests(fleet_id, fleet_data)
        
        # Select fleet certification standard
        standard = self.standards.get("fleet_standard")
        if not standard:
            standard = self._create_fleet_standard()
        
        # Calculate fleet score (minimum of all robots + fleet tests)
        fleet_score = self._calculate_fleet_score(fleet_results, robot_certificates)
        
        certificate = Certificate(
            certificate_id=f"FLEET-{uuid.uuid4().hex[:12].upper()}",
            type=CertificationType.ROBOT_FLEET,
            level=self._determine_fleet_certification_level(fleet_score),
            standard=standard,
            certified_entity=fleet_id,
            issuer=self.authority_name,
            issue_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=180),  # 6 months for fleets
            overall_score=fleet_score,
            requirement_results=fleet_results
        )
        
        self.certificates[certificate.certificate_id] = certificate
        
        return certificate
    
    def verify_certificate(self, certificate_id: str, 
                          entity_to_verify: str = None) -> Dict:
        """Verify a certificate is valid and not revoked"""
        certificate = self.certificates.get(certificate_id)
        
        if not certificate:
            # Check revoked certificates
            if certificate_id in self.revoked_certificates:
                return {
                    "valid": False,
                    "reason": "Certificate revoked",
                    "certificate_id": certificate_id
                }
            return {
                "valid": False,
                "reason": "Certificate not found",
                "certificate_id": certificate_id
            }
        
        # Check if expired
        if datetime.utcnow() > certificate.expiry_date:
            return {
                "valid": False,
                "reason": "Certificate expired",
                "expiry_date": certificate.expiry_date.isoformat(),
                "certificate_id": certificate_id
            }
        
        # Check if entity matches
        if entity_to_verify and entity_to_verify != certificate.certified_entity:
            return {
                "valid": False,
                "reason": f"Certificate issued for {certificate.certified_entity}, not {entity_to_verify}",
                "certificate_id": certificate_id
            }
        
        # Check blockchain validity if hash exists
        if certificate.blockchain_hash:
            blockchain_valid = self._verify_blockchain_hash(certificate)
            if not blockchain_valid:
                return {
                    "valid": False,
                    "reason": "Blockchain verification failed",
                    "certificate_id": certificate_id
                }
        
        return {
            "valid": True,
            "certificate": asdict(certificate),
            "days_remaining": (certificate.expiry_date - datetime.utcnow()).days
        }
    
    def revoke_certificate(self, certificate_id: str, reason: str):
        """Revoke a certificate"""
        certificate = self.certificates.get(certificate_id)
        if not certificate:
            raise ValueError(f"Certificate {certificate_id} not found")
        
        certificate.revocation_reason = reason
        certificate.revoked_date = datetime.utcnow()
        
        # Move to revoked set
        self.revoked_certificates.add(certificate_id)
        
        # Publish revocation
        self._publish_revocation(certificate_id, reason)
        
        return {
            "revoked": True,
            "certificate_id": certificate_id,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_certificate_details(self, certificate_id: str) -> Dict:
        """Get detailed certificate information"""
        certificate = self.certificates.get(certificate_id)
        if not certificate:
            raise ValueError(f"Certificate {certificate_id} not found")
        
        return asdict(certificate)
    
    def search_certificates(self, entity: str = None,
                          certificate_type: str = None,
                          level: str = None,
                          valid_only: bool = True) -> List[Dict]:
        """Search for certificates"""
        results = []
        
        for cert in self.certificates.values():
            # Apply filters
            if entity and entity not in cert.certified_entity:
                continue
            
            if certificate_type and cert.type.value != certificate_type:
                continue
            
            if level and cert.level.value != level:
                continue
            
            if valid_only:
                # Check if valid
                if datetime.utcnow() > cert.expiry_date:
                    continue
                if cert.certificate_id in self.revoked_certificates:
                    continue
            
            results.append(asdict(cert))
        
        return results
    
    async def renew_certificate(self, certificate_id: str, 
                              renewal_data: Dict = None) -> Certificate:
        """Renew an expiring certificate"""
        old_certificate = self.certificates.get(certificate_id)
        if not old_certificate:
            raise ValueError(f"Certificate {certificate_id} not found")
        
        # Check if eligible for renewal (not expired too long)
        days_expired = (datetime.utcnow() - old_certificate.expiry_date).days
        if days_expired > 30:
            raise ValueError(f"Certificate expired {days_expired} days ago, must re-certify")
        
        # Run renewal tests (usually simpler than full certification)
        renewal_results = await self._run_renewal_tests(old_certificate, renewal_data)
        
        # Check if still meets standards
        renewal_score = self._calculate_renewal_score(old_certificate, renewal_results)
        
        if renewal_score < old_certificate.standard.min_score * 0.9:  # 90% of original minimum
            raise ValueError(f"Renewal failed: Score {renewal_score} below threshold")
        
        # Create renewed certificate
        renewed_certificate = Certificate(
            certificate_id=f"RENEWED-{uuid.uuid4().hex[:12].upper()}",
            type=old_certificate.type,
            level=old_certificate.level,
            standard=old_certificate.standard,
            certified_entity=old_certificate.certified_entity,
            issuer=self.authority_name,
            issue_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=old_certificate.standard.validity_days),
            overall_score=renewal_score,
            requirement_results=renewal_results,
            blockchain_hash=self._generate_renewal_blockchain_hash(old_certificate, renewal_results)
        )
        
        # Store new certificate
        self.certificates[renewed_certificate.certificate_id] = renewed_certificate
        
        # Mark old certificate as superseded
        await self._mark_certificate_superseded(old_certificate.certificate_id, 
                                              renewed_certificate.certificate_id)
        
        return renewed_certificate
    
    # Internal methods
    def _load_standard_certifications(self):
        """Load standard certification templates"""
        
        # Industrial Robot Standard
        industrial_requirements = [
            SafetyRequirement(
                id="IND-001",
                description="Emergency stop functionality",
                linear_c_pattern="🛡️🔴⛔",
                test_procedure="Trigger emergency stop and verify robot stops within 250ms",
                passing_criteria="Stop within 250ms, no movement after stop",
                weight=0.15,
                mandatory=True
            ),
            SafetyRequirement(
                id="IND-002",
                description="Human proximity detection",
                linear_c_pattern="🟡🧍⚠️",
                test_procedure="Test proximity sensors with human dummy at varying distances",
                passing_criteria="Detect human within 0.5m, slow down within 1m",
                weight=0.12,
                mandatory=True
            ),
            SafetyRequirement(
                id="IND-003",
                description="Speed and force limiting",
                linear_c_pattern="🔵🚶",
                test_procedure="Test maximum speed and force in different modes",
                passing_criteria="Speed ≤ 1.0 m/s, force ≤ 150N in collaborative mode",
                weight=0.10,
                mandatory=True
            ),
            SafetyRequirement(
                id="IND-004",
                description="Software safety validation",
                linear_c_pattern="🟢🧠",
                test_procedure="Run 1000+ test scenarios with random inputs",
                passing_criteria="No safety violations in test suite",
                weight=0.13,
                mandatory=True
            ),
            SafetyRequirement(
                id="IND-005",
                description="Fault tolerance",
                linear_c_pattern="🛡️⚠️",
                test_procedure="Simulate sensor failures, power loss, communication drops",
                passing_criteria="Fail-safe operation in all simulated fault conditions",
                weight=0.10,
                mandatory=True
            )
        ]
        
        industrial_standard = CertificationStandard(
            id="iso_10218_ts_15066",
            name="Industrial Robot Safety (ISO 10218 + ISO/TS 15066)",
            version="2.1",
            description="Safety requirements for industrial robots including collaborative operation",
            requirements=industrial_requirements,
            min_score=85.0,
            validity_days=365,
            required_for=["manufacturing", "logistics", "assembly"],
            based_on=["ISO 10218-1", "ISO 10218-2", "ISO/TS 15066"]
        )
        
        self.standards[industrial_standard.id] = industrial_standard
        
        # Medical Robot Standard
        medical_requirements = [
            SafetyRequirement(
                id="MED-001",
                description="Sterile field maintenance",
                linear_c_pattern="🛡️🔵🧫",
                test_procedure="Test contamination prevention during procedures",
                passing_criteria="Zero contamination events in 100 test procedures",
                weight=0.20,
                mandatory=True
            ),
            SafetyRequirement(
                id="MED-002",
                description="Patient safety monitoring",
                linear_c_pattern="🧍💓⚠️",
                test_procedure="Monitor vital signs during robot operation",
                passing_criteria="Detect anomalies and stop within 10 seconds",
                weight=0.18,
                mandatory=True
            ),
            SafetyRequirement(
                id="MED-003",
                description="Precision and accuracy",
                linear_c_pattern="🎯📏",
                test_procedure="Test positional accuracy and repeatability",
                passing_criteria="Positional accuracy ≤ 0.1mm, repeatability ≤ 0.05mm",
                weight=0.15,
                mandatory=True
            )
        ]
        
        medical_standard = CertificationStandard(
            id="medical_robot_safety",
            name="Medical Robot Safety Standard",
            version="1.0",
            description="Safety requirements for medical and surgical robots",
            requirements=medical_requirements,
            min_score=95.0,
            validity_days=180,  # 6 months for medical
            required_for=["surgery", "rehabilitation", "diagnostics"],
            based_on=["IEC 60601-1", "ISO 13485", "FDA Guidance"]
        )
        
        self.standards[medical_standard.id] = medical_standard
        
        # Autonomous Vehicle Standard
        av_requirements = [
            SafetyRequirement(
                id="AV-001",
                description="Pedestrian detection and avoidance",
                linear_c_pattern="🛡️🚗👥",
                test_procedure="Test with pedestrian dummies in various scenarios",
                passing_criteria="100% detection, 0 collisions in test scenarios",
                weight=0.25,
                mandatory=True
            ),
            SafetyRequirement(
                id="AV-002",
                description="Obstacle detection",
                linear_c_pattern="⚠️📦",
                test_procedure="Test with various obstacle types and sizes",
                passing_criteria="Detect obstacles ≥ 10cm in height, avoid collisions",
                weight=0.20,
                mandatory=True
            )
        ]
        
        av_standard = CertificationStandard(
            id="sae_j3016_iso_26262",
            name="Autonomous Vehicle Safety (SAE J3016 + ISO 26262)",
            version="1.2",
            description="Safety requirements for autonomous vehicles",
            requirements=av_requirements,
            min_score=90.0,
            validity_days=90,  # 3 months for AV (rapidly changing field)
            required_for=["autonomous_vehicles", "drones", "agvs"],
            based_on=["SAE J3016", "ISO 26262", "UL 4600"]
        )
        
        self.standards[av_standard.id] = av_standard
    
    def _select_standard_for_robot(self, robot_model: str, test_data: Dict) -> CertificationStandard:
        """Select appropriate certification standard for robot"""
        robot_type = test_data.get("robot_type", "").lower()
        
        if "industrial" in robot_type or "cobot" in robot_type:
            return self.standards["iso_10218_ts_15066"]
        elif "medical" in robot_type or "surgical" in robot_type:
            return self.standards["medical_robot_safety"]
        elif "autonomous" in robot_type or "vehicle" in robot_type:
            return self.standards["sae_j3016_iso_26262"]
        else:
            # Default to industrial
            return self.standards["iso_10218_ts_15066"]
    
    async def _run_certification_tests(self, standard: CertificationStandard, 
                                     test_data: Dict) -> List[CertificationResult]:
        """Run certification tests based on standard"""
        results = []
        
        for requirement in standard.requirements:
            # Simulate test execution
            # In production, this would run actual tests
            score = 85.0 + hash(f"{requirement.id}{test_data.get('serial', '')}") % 15  # 85-100
            
            result = CertificationResult(
                requirement_id=requirement.id,
                passed=score >= 70,  # 70% to pass individual requirement
                score=score,
                evidence={
                    "test_data": test_data.get(requirement.id, {}),
                    "logs": f"Test executed for {requirement.id}",
                    "video_url": f"https://evidence.example.com/{requirement.id}"
                },
                notes=f"Test completed for {requirement.description}",
                timestamp=datetime.utcnow()
            )
            
            results.append(result)
        
        return results
    
    def _calculate_overall_score(self, standard: CertificationStandard,
                               results: List[CertificationResult]) -> float:
        """Calculate overall certification score"""
        if not results:
            return 0
        
        total_weighted_score = 0
        total_weight = 0
        
        for requirement in standard.requirements:
            result = next((r for r in results if r.requirement_id == requirement.id), None)
            if result:
                total_weighted_score += result.score * requirement.weight
                total_weight += requirement.weight
        
        if total_weight == 0:
            return 0
        
        return total_weighted_score / total_weight
    
    def _determine_certification_level(self, score: float, 
                                     standard: CertificationStandard) -> CertificationLevel:
        """Determine certification level based on score"""
        if score >= 95:
            return CertificationLevel.PREMIUM
        elif score >= 90:
            return CertificationLevel.ADVANCED
        elif score >= standard.min_score:
            return CertificationLevel.STANDARD
        else:
            return CertificationLevel.BASIC
    
    def _generate_blockchain_hash(self, robot_model: str, 
                                manufacturer: str,
                                results: List[CertificationResult]) -> str:
        """Generate blockchain hash for certificate proof"""
        data = {
            "robot_model": robot_model,
            "manufacturer": manufacturer,
            "results": [asdict(r) for r in results],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def _publish_certification(self, certificate: Certificate):
        """Publish certification to public registry"""
        print(f"Published certification: {certificate.certificate_id} for {certificate.certified_entity}")
    
    async def _validate_operator_qualifications(self, operator_id: str,
                                              operator_data: Dict,
                                              training_certificates: List[str]) -> bool:
        """Validate operator qualifications"""
        # Check minimum age
        if operator_data.get("age", 0) < 18:
            return False
        
        # Check required training
        required_training = ["basic_robot_safety", "emergency_procedures"]
        if training_certificates:
            for training in required_training:
                if training not in [tc.lower() for tc in training_certificates]:
                    return False
        
        # Check experience if provided
        if "experience_years" in operator_data and operator_data["experience_years"] < 1:
            return False
        
        return True
    
    async def _run_operator_safety_tests(self, operator_id: str,
                                       operator_data: Dict) -> List[CertificationResult]:
        """Run operator safety certification tests"""
        # Simulated tests
        tests = [
            CertificationResult(
                requirement_id="OP-001",
                passed=True,
                score=90.0,
                evidence={"test": "Written safety exam", "score": "45/50"},
                notes="Passed written exam",
                timestamp=datetime.utcnow()
            ),
            CertificationResult(
                requirement_id="OP-002",
                passed=True,
                score=85.0,
                evidence={"test": "Practical emergency stop", "time": "210ms"},
                notes="Emergency stop within required time",
                timestamp=datetime.utcnow()
            ),
            CertificationResult(
                requirement_id="OP-003",
                passed=True,
                score=88.0,
                evidence={"test": "Risk assessment", "score": "88%"},
                notes="Good risk assessment skills",
                timestamp=datetime.utcnow()
            )
        ]
        
        return tests
    
    def _calculate_operator_score(self, results: List[CertificationResult]) -> float:
        """Calculate operator certification score"""
        if not results:
            return 0
        
        return sum(r.score for r in results) / len(results)
    
    def _create_operator_standard(self) -> CertificationStandard:
        """Create operator certification standard"""
        requirements = [
            SafetyRequirement(
                id="OP-001",
                description="Safety knowledge exam",
                linear_c_pattern=None,
                test_procedure="50 question written exam on robot safety",
                passing_criteria="Score ≥ 80%",
                weight=0.4,
                mandatory=True
            ),
            SafetyRequirement(
                id="OP-002",
                description="Emergency procedures",
                linear_c_pattern="🛡️🔴⛔",
                test_procedure="Practical test of emergency stop procedures",
                passing_criteria="Stop robot within 250ms of emergency signal",
                weight=0.3,
                mandatory=True
            ),
            SafetyRequirement(
                id="OP-003",
                description="Risk assessment",
                linear_c_pattern="⚠️📋",
                test_procedure="Assess risks in given scenario",
                passing_criteria="Identify all major risks and propose mitigations",
                weight=0.3,
                mandatory=True
            )
        ]
        
        standard = CertificationStandard(
            id="operator_safety",
            name="Robot Operator Safety Certification",
            version="1.0",
            description="Certification for human robot operators",
            requirements=requirements,
            min_score=80.0,
            validity_days=365,
            required_for=["all_robot_operations"],
            based_on=["ANSI/RIA R15.06", "ISO 10218"]
        )
        
        self.standards[standard.id] = standard
        return standard
    
    async def _validate_fleet_certifications(self, fleet_id: str,
                                           robot_certificates: List[str]) -> bool:
        """Validate all robots in fleet have valid certifications"""
        if not robot_certificates:
            return False
        
        for cert_id in robot_certificates:
            verification = self.verify_certificate(cert_id)
            if not verification["valid"]:
                return False
        
        return True
    
    async def _run_fleet_safety_tests(self, fleet_id: str,
                                    fleet_data: Dict) -> List[CertificationResult]:
        """Run fleet-level safety tests"""
        # Simulated fleet tests
        tests = [
            CertificationResult(
                requirement_id="FLEET-001",
                passed=True,
                score=92.0,
                evidence={"test": "Fleet coordination", "collisions": "0"},
                notes="No collisions in multi-robot scenarios",
                timestamp=datetime.utcnow()
            ),
            CertificationResult(
                requirement_id="FLEET-002",
                passed=True,
                score=88.0,
                evidence={"test": "Communication reliability", "drop_rate": "0.1%"},
                notes="Reliable inter-robot communication",
                timestamp=datetime.utcnow()
            ),
            CertificationResult(
                requirement_id="FLEET-003",
                passed=True,
                score=90.0,
                evidence={"test": "Scalability", "max_robots": "50"},
                notes="Scales to 50 robots without performance degradation",
                timestamp=datetime.utcnow()
            )
        ]
        
        return tests
    
    def _create_fleet_standard(self) -> CertificationStandard:
        """Create fleet certification standard"""
        requirements = [
            SafetyRequirement(
                id="FLEET-001",
                description="Multi-robot coordination",
                linear_c_pattern="👥🤖",
                test_procedure="Test multiple robots operating in shared space",
                passing_criteria="No collisions or deadlocks",
                weight=0.4,
                mandatory=True
            ),
            SafetyRequirement(
                id="FLEET-002",
                description="Communication safety",
                linear_c_pattern="📡🛡️",
                test_procedure="Test communication reliability and security",
                passing_criteria="No safety-critical message loss, encrypted communications",
                weight=0.3,
                mandatory=True
            ),
            SafetyRequirement(
                id="FLEET-003",
                description="Scalability",
                linear_c_pattern="📈🤖",
                test_procedure="Test performance with increasing number of robots",
                passing_criteria="Linear or better scaling to at least 20 robots",
                weight=0.3,
                mandatory=True
            )
        ]
        
        standard = CertificationStandard(
            id="fleet_safety",
            name="Robot Fleet Safety Certification",
            version="1.0",
            description="Certification for multi-robot fleet operations",
            requirements=requirements,
            min_score=85.0,
            validity_days=180,
            required_for=["warehouse", "factory", "logistics"],
            based_on=["Multi-robot systems research"]
        )
        
        self.standards[standard.id] = standard
        return standard
    
    def _calculate_fleet_score(self, fleet_results: List[CertificationResult],
                             robot_certificates: List[str]) -> float:
        """Calculate fleet certification score"""
        # Average of fleet test scores
        if not fleet_results:
            return 0
        
        fleet_test_score = sum(r.score for r in fleet_results) / len(fleet_results)
        
        # Also consider individual robot certifications
        robot_scores = []
        for cert_id in robot_certificates:
            cert = self.certificates.get(cert_id)
            if cert:
                robot_scores.append(cert.overall_score)
        
        if robot_scores:
            avg_robot_score = sum(robot_scores) / len(robot_scores)
            # Weighted average: 60% fleet tests, 40% individual robots
            return fleet_test_score * 0.6 + avg_robot_score * 0.4
        else:
            return fleet_test_score
    
    def _determine_fleet_certification_level(self, score: float) -> CertificationLevel:
        """Determine fleet certification level"""
        if score >= 95:
            return CertificationLevel.PREMIUM
        elif score >= 90:
            return CertificationLevel.ADVANCED
        elif score >= 85:
            return CertificationLevel.STANDARD
        else:
            return CertificationLevel.BASIC
    
    def _verify_blockchain_hash(self, certificate: Certificate) -> bool:
        """Verify blockchain hash"""
        # In production, would verify against blockchain
        return certificate.blockchain_hash is not None
    
    def _publish_revocation(self, certificate_id: str, reason: str):
        """Publish certificate revocation"""
        print(f"Revoked certificate: {certificate_id} - Reason: {reason}")
    
    async def _run_renewal_tests(self, old_certificate: Certificate,
                               renewal_data: Dict) -> List[CertificationResult]:
        """Run renewal certification tests"""
        # Simpler than full certification
        results = []
        
        for requirement in old_certificate.standard.requirements[:3]:  # Test first 3 requirements
            score = old_certificate.overall_score * 0.95  # Slight degradation
            
            result = CertificationResult(
                requirement_id=requirement.id,
                passed=score >= 70,
                score=score,
                evidence={"renewal_test": True, "previous_score": old_certificate.overall_score},
                notes=f"Renewal test for {requirement.description}",
                timestamp=datetime.utcnow()
            )
            
            results.append(result)
        
        return results
    
    def _calculate_renewal_score(self, old_certificate: Certificate,
                               renewal_results: List[CertificationResult]) -> float:
        """Calculate renewal score"""
        if not renewal_results:
            return old_certificate.overall_score * 0.9  # Default 10% degradation
        
        renewal_avg = sum(r.score for r in renewal_results) / len(renewal_results)
        # Weighted average: 70% renewal tests, 30% previous score
        return renewal_avg * 0.7 + old_certificate.overall_score * 0.3
    
    def _generate_renewal_blockchain_hash(self, old_certificate: Certificate,
                                        renewal_results: List[CertificationResult]) -> str:
        """Generate blockchain hash for renewal"""
        data = {
            "original_certificate": old_certificate.certificate_id,
            "renewal_results": [asdict(r) for r in renewal_results],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def _mark_certificate_superseded(self, old_certificate_id: str,
                                         new_certificate_id: str):
        """Mark old certificate as superseded by new one"""
        print(f"Certificate {old_certificate_id} superseded by {new_certificate_id}")


# Certification Authority API
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    cert_app = FastAPI(title="Linear C Safety Certification Authority")
    
    cert_authority = SafetyCertificationAuthority()
    
    class RobotCertificationRequest(BaseModel):
        robot_model: str
        manufacturer: str
        robot_type: str
        test_data: Dict
    
    class OperatorCertificationRequest(BaseModel):
        operator_id: str
        operator_data: Dict
        training_certificates: List[str] = []
    
    class FleetCertificationRequest(BaseModel):
        fleet_id: str
        fleet_data: Dict
        robot_certificates: List[str]
    
    @cert_app.post("/api/v1/certification/robots")
    async def certify_robot(request: RobotCertificationRequest):
        """Certify a robot model"""
        try:
            certificate = await cert_authority.certify_robot_model(
                request.robot_model,
                request.manufacturer,
                request.test_data
            )
            
            return {
                "certificate_id": certificate.certificate_id,
                "level": certificate.level.value,
                "score": certificate.overall_score,
                "expiry_date": certificate.expiry_date.isoformat(),
                "validity_days": (certificate.expiry_date - certificate.issue_date).days
            }
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @cert_app.post("/api/v1/certification/operators")
    async def certify_operator(request: OperatorCertificationRequest):
        """Certify a robot operator"""
        try:
            certificate = await cert_authority.certify_operator(
                request.operator_id,
                request.operator_data,
                request.training_certificates
            )
            
            return {
                "certificate_id": certificate.certificate_id,
                "level": certificate.level.value,
                "score": certificate.overall_score,
                "expiry_date": certificate.expiry_date.isoformat()
            }
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @cert_app.post("/api/v1/certification/fleets")
    async def certify_fleet(request: FleetCertificationRequest):
        """Certify a robot fleet"""
        try:
            certificate = await cert_authority.certify_fleet(
                request.fleet_id,
                request.fleet_data,
                request.robot_certificates
            )
            
            return {
                "certificate_id": certificate.certificate_id,
                "level": certificate.level.value,
                "score": certificate.overall_score,
                "expiry_date": certificate.expiry_date.isoformat()
            }
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @cert_app.get("/api/v1/certification/verify/{certificate_id}")
    async def verify_certificate(certificate_id: str, entity: str = None):
        """Verify a certificate"""
        result = cert_authority.verify_certificate(certificate_id, entity)
        return result
    
    @cert_app.post("/api/v1/certification/revoke/{certificate_id}")
    async def revoke_certificate(certificate_id: str, reason: str):
        """Revoke a certificate"""
        try:
            result = cert_authority.revoke_certificate(certificate_id, reason)
            return result
            
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    @cert_app.post("/api/v1/certification/renew/{certificate_id}")
    async def renew_certificate(certificate_id: str):
        """Renew a certificate"""
        try:
            certificate = await cert_authority.renew_certificate(certificate_id)
            
            return {
                "new_certificate_id": certificate.certificate_id,
                "previous_certificate_id": certificate_id,
                "score": certificate.overall_score,
                "expiry_date": certificate.expiry_date.isoformat()
            }
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @cert_app.get("/api/v1/certification/search")
    async def search_certificates(
        entity: str = None,
        type: str = None,
        level: str = None,
        valid_only: bool = True
    ):
        """Search for certificates"""
        results = cert_authority.search_certificates(entity, type, level, valid_only)
        return results

except ImportError:
    # FastAPI not installed - authority class still works standalone
    pass
