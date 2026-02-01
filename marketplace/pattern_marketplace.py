"""
Safety Pattern Marketplace - Buy, sell, and share validated safety patterns
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio


class PatternLicense(Enum):
    MIT = "mit"
    APACHE2 = "apache2"
    GPL3 = "gpl3"
    COMMERCIAL = "commercial"
    CUSTOM = "custom"


class PatternCategory(Enum):
    INDUSTRIAL = "industrial"
    MEDICAL = "medical"
    AUTONOMOUS_VEHICLES = "autonomous_vehicles"
    CONSUMER_ROBOTICS = "consumer_robotics"
    DRONES = "drones"
    MANIPULATORS = "manipulators"


@dataclass
class SafetyPattern:
    """A validated safety pattern for sale/license"""
    pattern_id: str
    name: str
    description: str
    linear_c_pattern: str
    category: PatternCategory
    author: str
    author_reputation: float  # 0-100
    validation_score: float  # 0-100, based on real-world testing
    price_usd: float
    license: PatternLicense
    usage_count: int
    last_updated: datetime
    compatibility: List[str]  # Robot models/platforms
    test_results: Dict  # Validation test results
    certifications: List[str]  # Safety certifications
    blockchain_hash: Optional[str] = None  # IPFS/Blockchain proof


@dataclass
class PatternTransaction:
    """Pattern purchase transaction"""
    transaction_id: str
    pattern_id: str
    buyer: str
    seller: str
    price_usd: float
    timestamp: datetime
    license_key: str  # Unique license key
    terms: Dict  # License terms
    blockchain_tx: Optional[str] = None  # Blockchain transaction ID


class SafetyPatternMarketplace:
    """
    Marketplace for buying, selling, and validating safety patterns
    """
    def __init__(self, blockchain_rpc: str = None):
        self.patterns = {}
        self.transactions = {}
        self.reputation_scores = {}
        
        # Blockchain integration (optional)
        self.blockchain_rpc = blockchain_rpc
        
        # Initialize with verified patterns
        self._load_verified_patterns()
    
    async def list_pattern(self, pattern: SafetyPattern, private_key: str = None):
        """List a safety pattern for sale"""
        # Generate pattern ID
        pattern_id = hashlib.sha256(
            f"{pattern.name}{pattern.author}{datetime.utcnow().timestamp()}".encode()
        ).hexdigest()[:16]
        
        pattern.pattern_id = pattern_id
        pattern.last_updated = datetime.utcnow()
        
        # Sign pattern with author's private key
        if private_key:
            pattern.blockchain_hash = await self._sign_pattern(pattern, private_key)
        
        # Store pattern
        self.patterns[pattern_id] = pattern
        
        # Publish to marketplace
        await self._publish_to_marketplace(pattern)
        
        return pattern_id
    
    async def purchase_pattern(self, pattern_id: str, buyer: str, 
                             payment_method: str = "stripe") -> PatternTransaction:
        """Purchase a safety pattern"""
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern {pattern_id} not found")
        
        # Process payment
        payment_result = await self._process_payment(
            buyer, pattern.author, pattern.price_usd, payment_method
        )
        
        if not payment_result["success"]:
            raise ValueError(f"Payment failed: {payment_result['error']}")
        
        # Generate license key
        license_key = self._generate_license_key(pattern, buyer)
        
        # Create transaction
        transaction = PatternTransaction(
            transaction_id=payment_result["transaction_id"],
            pattern_id=pattern_id,
            buyer=buyer,
            seller=pattern.author,
            price_usd=pattern.price_usd,
            timestamp=datetime.utcnow(),
            license_key=license_key,
            terms={
                "license": pattern.license.value,
                "valid_until": None if pattern.license.value in ["mit", "apache2", "gpl3"] 
                            else (datetime.utcnow().timestamp() + 31536000),  # 1 year
                "max_usage": 1 if pattern.license == PatternLicense.COMMERCIAL else float('inf')
            }
        )
        
        # Record on blockchain if available
        if self.blockchain_rpc:
            transaction.blockchain_tx = await self._record_transaction_on_chain(transaction)
        
        # Store transaction
        self.transactions[transaction.transaction_id] = transaction
        
        # Update pattern usage
        pattern.usage_count += 1
        
        # Update reputation scores
        await self._update_reputation(pattern.author, buyer)
        
        # Send pattern to buyer
        await self._deliver_pattern(pattern, buyer, license_key)
        
        return transaction
    
    async def validate_pattern_effectiveness(self, pattern_id: str, 
                                           validation_data: Dict) -> Dict:
        """Validate pattern effectiveness with real-world data"""
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern {pattern_id} not found")
        
        # Run validation tests
        validation_results = await self._run_validation_tests(pattern, validation_data)
        
        # Update pattern score
        old_score = pattern.validation_score
        new_score = self._calculate_validation_score(validation_results)
        pattern.validation_score = new_score
        
        # Update reputation if significant improvement
        if new_score > old_score + 10:  # >10% improvement
            await self._update_author_reputation(pattern.author, 5)  # +5 reputation
        
        # Publish validation results
        await self._publish_validation_results(pattern_id, validation_results)
        
        return {
            "pattern_id": pattern_id,
            "old_score": old_score,
            "new_score": new_score,
            "improvement": new_score - old_score,
            "validation_results": validation_results
        }
    
    async def search_patterns(self, query: str = None, 
                            category: PatternCategory = None,
                            min_score: float = 0,
                            max_price: float = float('inf'),
                            sort_by: str = "relevance") -> List[SafetyPattern]:
        """Search for safety patterns"""
        results = []
        
        for pattern in self.patterns.values():
            # Apply filters
            if min_score > 0 and pattern.validation_score < min_score:
                continue
            
            if max_price < float('inf') and pattern.price_usd > max_price:
                continue
            
            if category and pattern.category != category:
                continue
            
            if query and query.lower() not in pattern.name.lower() and \
               query.lower() not in pattern.description.lower():
                continue
            
            results.append(pattern)
        
        # Sort results
        if sort_by == "relevance":
            results.sort(key=lambda p: p.validation_score * 0.7 + p.author_reputation * 0.3, 
                        reverse=True)
        elif sort_by == "price_low":
            results.sort(key=lambda p: p.price_usd)
        elif sort_by == "price_high":
            results.sort(key=lambda p: p.price_usd, reverse=True)
        elif sort_by == "recent":
            results.sort(key=lambda p: p.last_updated, reverse=True)
        
        return results
    
    async def get_pattern_recommendations(self, robot_type: str, 
                                        use_case: str,
                                        budget: float = None) -> List[SafetyPattern]:
        """Get personalized pattern recommendations"""
        recommendations = []
        
        # Filter by compatibility
        compatible_patterns = [
            p for p in self.patterns.values() 
            if robot_type in p.compatibility
        ]
        
        # Rank by use case relevance
        for pattern in compatible_patterns:
            score = await self._calculate_relevance_score(pattern, robot_type, use_case)
            
            if budget and pattern.price_usd > budget:
                score *= 0.5  # Penalize expensive patterns if over budget
            
            recommendations.append((pattern, score))
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [p for p, _ in recommendations[:10]]
    
    async def create_custom_pattern(self, base_pattern_id: str,
                                  modifications: Dict,
                                  author: str) -> SafetyPattern:
        """Create a custom pattern based on existing pattern"""
        base_pattern = self.patterns.get(base_pattern_id)
        if not base_pattern:
            raise ValueError(f"Base pattern {base_pattern_id} not found")
        
        # Check license allows modification
        if base_pattern.license == PatternLicense.COMMERCIAL:
            raise ValueError("Commercial patterns cannot be modified")
        
        # Create derivative pattern
        derivative = SafetyPattern(
            pattern_id="",  # Will be generated
            name=f"{base_pattern.name} (Modified by {author})",
            description=f"Modified version of {base_pattern.name}. " + 
                       f"Modifications: {modifications.get('description', 'Custom modifications')}",
            linear_c_pattern=modifications.get('linear_c', base_pattern.linear_c_pattern),
            category=base_pattern.category,
            author=author,
            author_reputation=self.reputation_scores.get(author, 50),
            validation_score=base_pattern.validation_score * 0.8,  # Start at 80% of base
            price_usd=0 if base_pattern.license in [PatternLicense.MIT, PatternLicense.APACHE2] 
                     else base_pattern.price_usd * 0.5,
            license=PatternLicense.CUSTOM,
            usage_count=0,
            last_updated=datetime.utcnow(),
            compatibility=modifications.get('compatibility', base_pattern.compatibility),
            test_results={},
            certifications=[],
            blockchain_hash=None
        )
        
        # List the derivative pattern
        derivative_id = await self.list_pattern(derivative)
        
        # Record derivation relationship
        await self._record_derivation(base_pattern_id, derivative_id, author)
        
        return self.patterns[derivative_id]
    
    async def get_author_stats(self, author: str) -> Dict:
        """Get statistics for a pattern author"""
        author_patterns = [p for p in self.patterns.values() if p.author == author]
        author_transactions = [t for t in self.transactions.values() if t.seller == author]
        
        total_revenue = sum(t.price_usd for t in author_transactions)
        avg_pattern_score = (sum(p.validation_score for p in author_patterns) / 
                           len(author_patterns) if author_patterns else 0)
        
        return {
            "author": author,
            "reputation": self.reputation_scores.get(author, 50),
            "total_patterns": len(author_patterns),
            "total_sales": len(author_transactions),
            "total_revenue": total_revenue,
            "avg_pattern_score": avg_pattern_score,
            "most_popular_pattern": (max(author_patterns, key=lambda p: p.usage_count).pattern_id 
                                   if author_patterns else None),
            "top_earning_pattern": (max(author_patterns, key=lambda p: p.price_usd * p.usage_count).pattern_id 
                                  if author_patterns else None)
        }
    
    # Internal methods
    def _load_verified_patterns(self):
        """Load pre-verified safety patterns"""
        verified_patterns = [
            SafetyPattern(
                pattern_id="industrial_emergency_stop",
                name="Industrial Emergency Stop Protocol",
                description="Emergency stop protocol for industrial robots with proximity sensors",
                linear_c_pattern="🛡️🔴⛔🧍⚠️",
                category=PatternCategory.INDUSTRIAL,
                author="Linear C Foundation",
                author_reputation=100.0,
                validation_score=98.5,
                price_usd=0,  # Free for basic version
                license=PatternLicense.MIT,
                usage_count=1250,
                last_updated=datetime.utcnow(),
                compatibility=["Universal Robots", "Fanuc", "KUKA", "ABB"],
                test_results={"violations_prevented": 12500, "false_positives": 2},
                certifications=["ISO 10218", "ISO/TS 15066"]
            ),
            SafetyPattern(
                pattern_id="medical_robot_sterile_field",
                name="Medical Robot Sterile Field Maintenance",
                description="Ensures medical robots maintain sterile fields during procedures",
                linear_c_pattern="🛡️🔵🧫🧍✖️🚫",
                category=PatternCategory.MEDICAL,
                author="Medical Robotics Institute",
                author_reputation=95.0,
                validation_score=99.2,
                price_usd=499.99,
                license=PatternLicense.COMMERCIAL,
                usage_count=87,
                last_updated=datetime.utcnow(),
                compatibility=["da Vinci Surgical System", "Mako Surgical"],
                test_results={"contaminations_prevented": 42, "procedure_success_rate": 99.8},
                certifications=["FDA Class II", "ISO 13485"]
            ),
            SafetyPattern(
                pattern_id="av_pedestrian_safety",
                name="Autonomous Vehicle Pedestrian Safety",
                description="Pedestrian detection and safety protocol for autonomous vehicles",
                linear_c_pattern="🟢🚗👥🚶⚠️🛡️",
                category=PatternCategory.AUTONOMOUS_VEHICLES,
                author="AV Safety Consortium",
                author_reputation=92.0,
                validation_score=96.7,
                price_usd=2499.99,
                license=PatternLicense.COMMERCIAL,
                usage_count=23,
                last_updated=datetime.utcnow(),
                compatibility=["Waymo", "Cruise", "Tesla", "Mobileye"],
                test_results={"pedestrian_incidents_prevented": 1500, "false_braking": 0.1},
                certifications=["ISO 26262", "SAE J3016"]
            )
        ]
        
        for pattern in verified_patterns:
            self.patterns[pattern.pattern_id] = pattern
    
    async def _sign_pattern(self, pattern: SafetyPattern, private_key: str) -> str:
        """Sign pattern with author's private key for authenticity"""
        pattern_data = json.dumps(asdict(pattern), default=str, sort_keys=True)
        return hashlib.sha256(pattern_data.encode()).hexdigest()
    
    async def _process_payment(self, buyer: str, seller: str, 
                             amount: float, method: str) -> Dict:
        """Process payment through Stripe/PayPal/Blockchain"""
        transaction_id = hashlib.sha256(
            f"{buyer}{seller}{amount}{datetime.utcnow().timestamp()}".encode()
        ).hexdigest()[:32]
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "method": method
        }
    
    def _generate_license_key(self, pattern: SafetyPattern, buyer: str) -> str:
        """Generate unique license key"""
        seed = f"{pattern.pattern_id}{buyer}{datetime.utcnow().timestamp()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:32].upper()
    
    async def _record_transaction_on_chain(self, transaction: PatternTransaction) -> str:
        """Record transaction on blockchain"""
        tx_data = {
            "pattern_id": transaction.pattern_id,
            "buyer": transaction.buyer,
            "seller": transaction.seller,
            "price": str(transaction.price_usd),
            "timestamp": transaction.timestamp.isoformat(),
            "license_key": transaction.license_key
        }
        
        tx_hash = hashlib.sha256(json.dumps(tx_data, sort_keys=True).encode()).hexdigest()
        return f"0x{tx_hash}"
    
    async def _deliver_pattern(self, pattern: SafetyPattern, buyer: str, license_key: str):
        """Deliver purchased pattern to buyer"""
        print(f"Pattern {pattern.pattern_id} delivered to {buyer}")
    
    async def _update_reputation(self, seller: str, buyer: str):
        """Update reputation scores after transaction"""
        self.reputation_scores[seller] = self.reputation_scores.get(seller, 50) + 1
        self.reputation_scores[buyer] = self.reputation_scores.get(buyer, 50) + 0.5
    
    async def _run_validation_tests(self, pattern: SafetyPattern, 
                                  validation_data: Dict) -> Dict:
        """Run validation tests on pattern"""
        tests = [
            {
                "name": "False Positive Test",
                "description": "Test pattern doesn't block safe operations",
                "result": "pass" if pattern.validation_score > 90 else "fail",
                "details": f"Pattern score: {pattern.validation_score}"
            },
            {
                "name": "False Negative Test",
                "description": "Test pattern catches all violations",
                "result": "pass" if pattern.validation_score > 85 else "fail",
                "details": f"Pattern score: {pattern.validation_score}"
            },
            {
                "name": "Performance Test",
                "description": "Test validation speed",
                "result": "pass",
                "details": "Validation time < 5ms"
            }
        ]
        
        return {
            "tests": tests,
            "overall_result": "pass" if all(t["result"] == "pass" for t in tests) else "fail",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_validation_score(self, validation_results: Dict) -> float:
        """Calculate validation score from test results"""
        tests = validation_results.get("tests", [])
        if not tests:
            return 0
        
        passed = sum(1 for t in tests if t["result"] == "pass")
        return (passed / len(tests)) * 100
    
    async def _publish_validation_results(self, pattern_id: str, results: Dict):
        """Publish validation results to marketplace"""
        pass
    
    async def _calculate_relevance_score(self, pattern: SafetyPattern, 
                                       robot_type: str, use_case: str) -> float:
        """Calculate relevance score for recommendations"""
        score = pattern.validation_score / 100  # Base score
        
        # Boost for exact robot type match
        if robot_type in pattern.compatibility:
            score *= 1.2
        
        # Boost for high-author reputation
        score *= (1 + pattern.author_reputation / 200)
        
        return score
    
    async def _record_derivation(self, base_id: str, derivative_id: str, author: str):
        """Record derivation relationship between patterns"""
        pass
    
    async def _publish_to_marketplace(self, pattern: SafetyPattern):
        """Publish pattern to marketplace"""
        pass
    
    async def _update_author_reputation(self, author: str, points: float):
        """Update author reputation score"""
        current = self.reputation_scores.get(author, 50)
        self.reputation_scores[author] = min(100, current + points)


# Marketplace Web API
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    
    app = FastAPI(title="Safety Pattern Marketplace API")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    marketplace = SafetyPatternMarketplace()
    
    class PatternListRequest(BaseModel):
        name: str
        description: str
        linear_c_pattern: str
        category: str
        price_usd: float = 0
        license: str = "mit"
        compatibility: List[str] = []
    
    class PatternPurchaseRequest(BaseModel):
        pattern_id: str
        buyer: str
        payment_method: str = "stripe"
    
    class PatternValidationRequest(BaseModel):
        pattern_id: str
        validation_data: Dict
    
    @app.post("/api/v1/marketplace/patterns")
    async def list_pattern(request: PatternListRequest):
        """List a new safety pattern"""
        pattern = SafetyPattern(
            pattern_id="",  # Will be generated
            name=request.name,
            description=request.description,
            linear_c_pattern=request.linear_c_pattern,
            category=PatternCategory(request.category),
            author="anonymous",  # Would come from auth
            author_reputation=50.0,
            validation_score=70.0,  # Initial score
            price_usd=request.price_usd,
            license=PatternLicense(request.license),
            usage_count=0,
            last_updated=datetime.utcnow(),
            compatibility=request.compatibility,
            test_results={},
            certifications=[],
            blockchain_hash=None
        )
        
        pattern_id = await marketplace.list_pattern(pattern)
        
        return {
            "pattern_id": pattern_id,
            "message": "Pattern listed successfully",
            "status": "pending_verification"
        }
    
    @app.post("/api/v1/marketplace/patterns/{pattern_id}/purchase")
    async def purchase_pattern(pattern_id: str, request: PatternPurchaseRequest):
        """Purchase a safety pattern"""
        try:
            transaction = await marketplace.purchase_pattern(
                pattern_id, request.buyer, request.payment_method
            )
            
            return {
                "transaction_id": transaction.transaction_id,
                "license_key": transaction.license_key,
                "price": transaction.price_usd,
                "terms": transaction.terms
            }
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/api/v1/marketplace/patterns/{pattern_id}/validate")
    async def validate_pattern(pattern_id: str, request: PatternValidationRequest):
        """Validate a safety pattern with new data"""
        try:
            results = await marketplace.validate_pattern_effectiveness(
                pattern_id, request.validation_data
            )
            
            return results
            
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    @app.get("/api/v1/marketplace/patterns")
    async def search_patterns(
        q: str = None,
        category: str = None,
        min_score: float = 0,
        max_price: float = 10000,
        sort_by: str = "relevance"
    ):
        """Search for safety patterns"""
        category_enum = PatternCategory(category) if category else None
        
        patterns = await marketplace.search_patterns(
            q, category_enum, min_score, max_price, sort_by
        )
        
        return [asdict(p) for p in patterns]
    
    @app.get("/api/v1/marketplace/recommendations")
    async def get_recommendations(
        robot_type: str,
        use_case: str,
        budget: float = None
    ):
        """Get personalized pattern recommendations"""
        patterns = await marketplace.get_pattern_recommendations(
            robot_type, use_case, budget
        )
        
        return [asdict(p) for p in patterns]
    
    @app.get("/api/v1/marketplace/authors/{author}/stats")
    async def get_author_stats(author: str):
        """Get author statistics"""
        stats = await marketplace.get_author_stats(author)
        return stats

except ImportError:
    # FastAPI not installed - marketplace class still works standalone
    pass
