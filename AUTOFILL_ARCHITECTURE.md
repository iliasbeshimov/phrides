# Robust Autofill Architecture with Cascading Logic

## Overview

A multi-layered, cascading autofill system designed for maximum success rate across diverse dealership website forms, with Amazon Nova Act as the final fallback for complex scenarios.

## Architecture Principles

1. **Cascading Strategies**: Multiple layers of form detection and filling approaches
2. **Progressive Complexity**: Start simple, escalate to sophisticated methods
3. **Adaptive Learning**: Learn from successes and failures to improve mappings
4. **Comprehensive Logging**: Track every step for debugging and optimization
5. **Graceful Degradation**: Always have a fallback strategy

## Cascading Strategy Layers

### Layer 1: Pre-mapped Form Strategies (Fastest)
**Success Rate Goal: 60-70%**

```python
class PreMappedStrategy:
    """Use pre-configured form mappings for known dealership patterns"""
    
    strategies = {
        "stellantis_dealer": {
            "form_selector": "#contact-form, .contact-form, form[name='contact']",
            "fields": {
                "first_name": ["input[name='firstName']", "input[name='fname']", "#firstName"],
                "last_name": ["input[name='lastName']", "input[name='lname']", "#lastName"],
                "email": ["input[type='email']", "input[name='email']", "#email"],
                "phone": ["input[type='tel']", "input[name='phone']", "#phone"],
                "message": ["textarea[name='message']", "textarea[name='comments']", "#message"]
            },
            "vehicle_interest": {
                "selector": "select[name='vehicleOfInterest'], select[name='model']",
                "jeep_options": ["Jeep", "JEEP", "jeep", "All Jeep Models"]
            },
            "submit": ["button[type='submit']", "input[type='submit']", ".submit-btn"]
        },
        
        "cdk_dealer": {
            # CDK Global dealer platform patterns
            "form_selector": ".lead-form, #leadForm, .inquiry-form",
            "fields": {
                "first_name": ["#lead_customer_first_name", "input[name*='first']"],
                "last_name": ["#lead_customer_last_name", "input[name*='last']"],
                "email": ["#lead_customer_email", "input[name*='email']"],
                "phone": ["#lead_customer_primary_phone", "input[name*='phone']"]
            }
        },
        
        "autotrader_dealer": {
            # AutoTrader/Cox Automotive patterns
            "form_selector": ".at-form, #contact_form",
            "fields": {
                "first_name": ["#at_first_name", "input[placeholder*='First']"],
                "last_name": ["#at_last_name", "input[placeholder*='Last']"]
            }
        }
    }
```

### Layer 2: Semantic Form Detection (Smart)
**Success Rate Goal: 80-85%**

```python
class SemanticFormStrategy:
    """Intelligent form field detection using semantic analysis"""
    
    def detect_form_fields(self, page):
        """Use semantic patterns to identify form fields"""
        
        field_detectors = {
            "first_name": {
                "selectors": [
                    "input[type='text']",
                    "input:not([type])"
                ],
                "semantic_patterns": [
                    r"first.*name",
                    r"fname",
                    r"given.*name",
                    r"contact.*first"
                ],
                "placeholder_patterns": [
                    r"first.*name",
                    r"your.*first.*name",
                    r"enter.*first"
                ],
                "label_patterns": [
                    "first name",
                    "first",
                    "given name"
                ]
            },
            
            "last_name": {
                "selectors": ["input[type='text']"],
                "semantic_patterns": [
                    r"last.*name",
                    r"lname",
                    r"surname",
                    r"family.*name"
                ]
            },
            
            "email": {
                "selectors": [
                    "input[type='email']",
                    "input[type='text']"
                ],
                "semantic_patterns": [
                    r"email",
                    r"e-mail",
                    r"mail"
                ],
                "validation_patterns": [
                    r"@",  # Check if field expects @ symbol
                ]
            },
            
            "phone": {
                "selectors": [
                    "input[type='tel']",
                    "input[type='text']"
                ],
                "semantic_patterns": [
                    r"phone",
                    r"tel",
                    r"mobile",
                    r"cell"
                ]
            },
            
            "message": {
                "selectors": ["textarea"],
                "semantic_patterns": [
                    r"message",
                    r"comment",
                    r"inquiry",
                    r"details",
                    r"notes"
                ]
            },
            
            "vehicle_interest": {
                "selectors": ["select"],
                "semantic_patterns": [
                    r"vehicle",
                    r"model",
                    r"interest",
                    r"looking.*for"
                ]
            }
        }
        
        return self._match_fields_semantically(page, field_detectors)
```

### Layer 3: Visual/Layout Analysis (Advanced)
**Success Rate Goal: 90-95%**

```python
class VisualFormStrategy:
    """Use visual layout patterns and field positioning"""
    
    def analyze_form_visually(self, page):
        """Analyze form layout and field positioning"""
        
        # Take screenshot for visual analysis
        screenshot = page.screenshot()
        
        # Detect form containers
        form_containers = page.locator("form, .form, div[class*='contact'], div[id*='contact']").all()
        
        for container in form_containers:
            fields = self._analyze_container_layout(container)
            
            # Use spatial relationships
            form_analysis = {
                "form_bounds": container.bounding_box(),
                "field_positions": self._get_field_positions(fields),
                "visual_hierarchy": self._analyze_visual_hierarchy(fields),
                "field_groupings": self._detect_field_groups(fields)
            }
            
            # Apply layout-based detection
            field_mapping = self._map_fields_by_layout(form_analysis)
            
            if self._validate_field_mapping(field_mapping):
                return field_mapping
        
        return None
        
    def _analyze_visual_hierarchy(self, fields):
        """Analyze visual hierarchy of form fields"""
        return {
            "top_to_bottom": sorted(fields, key=lambda f: f.bounding_box()["y"]),
            "left_to_right": sorted(fields, key=lambda f: f.bounding_box()["x"]),
            "field_sizes": {f: f.bounding_box() for f in fields}
        }
```

### Layer 4: Machine Learning Form Recognition (Intelligent)
**Success Rate Goal: 95-97%**

```python
class MLFormStrategy:
    """Machine learning-based form field classification"""
    
    def __init__(self):
        self.field_classifier = self._load_trained_model()
        self.form_pattern_matcher = self._load_pattern_model()
    
    def classify_form_fields(self, page):
        """Use ML models to classify form fields"""
        
        # Extract features for each form field
        form_fields = page.locator("input, textarea, select").all()
        
        classified_fields = {}
        
        for field in form_fields:
            features = self._extract_field_features(field)
            
            # Classify field type using trained model
            field_type = self.field_classifier.predict(features)
            confidence = self.field_classifier.predict_proba(features)
            
            if confidence > 0.8:  # High confidence threshold
                classified_fields[field_type] = {
                    "element": field,
                    "confidence": confidence,
                    "features": features
                }
        
        return classified_fields
    
    def _extract_field_features(self, field):
        """Extract features for ML classification"""
        return {
            # Element attributes
            "tag_name": field.tag_name,
            "type": field.get_attribute("type"),
            "name": field.get_attribute("name") or "",
            "id": field.get_attribute("id") or "",
            "class": field.get_attribute("class") or "",
            "placeholder": field.get_attribute("placeholder") or "",
            
            # Text content analysis
            "label_text": self._get_associated_label_text(field),
            "surrounding_text": self._get_surrounding_text(field),
            
            # Visual features
            "position": field.bounding_box(),
            "size": {"width": field.bounding_box()["width"], "height": field.bounding_box()["height"]},
            "is_required": field.get_attribute("required") is not None,
            
            # Context features
            "form_context": self._analyze_form_context(field),
            "field_order": self._get_field_order_in_form(field)
        }
```

### Layer 5: Amazon Nova Act Integration (Ultimate Fallback)
**Success Rate Goal: 99%+**

```python
class NovaActStrategy:
    """Amazon Nova Act for complex form interactions"""
    
    def __init__(self):
        self.nova_client = self._initialize_nova_client()
    
    async def fill_form_with_nova_act(self, page, user_data):
        """Use Nova Act for intelligent form filling"""
        
        # Take screenshot for visual context
        screenshot = await page.screenshot()
        
        # Prepare Nova Act prompt
        prompt = f"""
        You are helping to fill out a car dealership contact form. Here's what you need to do:
        
        USER DATA TO ENTER:
        - First Name: {user_data['first_name']}
        - Last Name: {user_data['last_name']}
        - Email: {user_data['email']}
        - Phone: {user_data['phone']}
        - Vehicle Interest: Jeep
        - Message: {user_data['message']}
        
        INSTRUCTIONS:
        1. Locate the contact form on this dealership website
        2. Fill in all the fields with the provided information
        3. Handle any dropdowns (select "Jeep" or "All Models" for vehicle interest)
        4. Check any required consent/privacy checkboxes
        5. Submit the form
        6. Confirm successful submission or report any errors
        
        Be careful with:
        - Required field indicators (*)
        - Dropdown options that might be worded differently
        - Multiple forms on the same page (choose the main contact form)
        - CAPTCHAs (report if encountered)
        """
        
        try:
            # Execute Nova Act automation
            result = await self.nova_client.execute_task(
                page=page,
                prompt=prompt,
                screenshot=screenshot,
                max_steps=20,
                timeout=60
            )
            
            return {
                "success": result.success,
                "steps_taken": result.steps,
                "final_state": result.final_state,
                "errors": result.errors,
                "screenshots": result.screenshots
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_needed": True
            }
```

## Cascading Execution Engine

```python
class CascadingAutofillEngine:
    """Main engine that orchestrates cascading strategies"""
    
    def __init__(self):
        self.strategies = [
            PreMappedStrategy(),
            SemanticFormStrategy(),
            VisualFormStrategy(),
            MLFormStrategy(),
            NovaActStrategy()
        ]
        
        self.logger = StructuredLogger("autofill_engine")
    
    async def fill_dealership_form(self, page, dealership_info, user_data):
        """Execute cascading autofill strategies"""
        
        request_id = str(uuid.uuid4())
        
        self.logger.info("Autofill process started", {
            "operation": "autofill_start",
            "request_id": request_id,
            "dealership_id": dealership_info["id"],
            "dealership_name": dealership_info["name"],
            "url": page.url,
            "strategies_available": len(self.strategies)
        })
        
        for i, strategy in enumerate(self.strategies, 1):
            strategy_name = strategy.__class__.__name__
            
            self.logger.info(f"Attempting strategy {i}", {
                "operation": "strategy_attempt",
                "request_id": request_id,
                "strategy": strategy_name,
                "strategy_layer": i,
                "previous_failures": i - 1
            })
            
            try:
                # Add timeout and error handling
                with timeout(30):  # 30 second timeout per strategy
                    result = await strategy.fill_form(page, user_data)
                
                if result.success:
                    self.logger.info("Autofill successful", {
                        "operation": "autofill_success",
                        "request_id": request_id,
                        "successful_strategy": strategy_name,
                        "attempts_needed": i,
                        "form_fields_filled": len(result.filled_fields),
                        "submission_confirmed": result.submission_confirmed,
                        "duration_ms": result.duration_ms
                    })
                    
                    # Update strategy success metrics
                    self._update_strategy_metrics(strategy_name, dealership_info, True)
                    
                    return result
                
                else:
                    self.logger.warning("Strategy failed", {
                        "operation": "strategy_failed",
                        "request_id": request_id,
                        "strategy": strategy_name,
                        "error": result.error,
                        "partial_success": result.partial_fields_filled
                    })
                    
            except TimeoutError:
                self.logger.error("Strategy timed out", {
                    "operation": "strategy_timeout",
                    "request_id": request_id,
                    "strategy": strategy_name,
                    "timeout_seconds": 30
                })
                
            except Exception as e:
                self.logger.error("Strategy crashed", {
                    "operation": "strategy_error",
                    "request_id": request_id,
                    "strategy": strategy_name,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "stack_trace": traceback.format_exc()
                })
        
        # All strategies failed
        self.logger.error("All autofill strategies failed", {
            "operation": "autofill_complete_failure",
            "request_id": request_id,
            "dealership_id": dealership_info["id"],
            "strategies_attempted": len(self.strategies),
            "url": page.url
        })
        
        return AutofillResult(
            success=False,
            error="All autofill strategies exhausted",
            strategies_attempted=len(self.strategies)
        )
```

## Adaptive Learning System

```python
class AdaptiveLearningSystem:
    """Learn from successes and failures to improve autofill accuracy"""
    
    def __init__(self):
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
    
    def record_success(self, dealership_info, strategy_used, form_mapping):
        """Record successful autofill for learning"""
        
        pattern = {
            "dealership_name": dealership_info["name"],
            "website_domain": extract_domain(dealership_info["website"]),
            "strategy": strategy_used,
            "form_selector": form_mapping["form_selector"],
            "field_mappings": form_mapping["fields"],
            "timestamp": datetime.now().isoformat()
        }
        
        domain = extract_domain(dealership_info["website"])
        self.success_patterns[domain].append(pattern)
        
        # Update pre-mapped strategies
        self._update_pre_mapped_patterns(domain, pattern)
    
    def predict_best_strategy(self, dealership_info):
        """Predict which strategy is most likely to succeed"""
        
        domain = extract_domain(dealership_info["website"])
        
        if domain in self.success_patterns:
            # Analyze historical success patterns
            patterns = self.success_patterns[domain]
            strategy_scores = defaultdict(int)
            
            for pattern in patterns:
                strategy_scores[pattern["strategy"]] += 1
            
            # Return strategies sorted by historical success rate
            return sorted(strategy_scores.items(), key=lambda x: x[1], reverse=True)
        
        return None  # Use default cascade order
```

## Testing & Validation Framework

```python
class AutofillTestFramework:
    """Comprehensive testing framework for autofill strategies"""
    
    def __init__(self):
        self.test_dealerships = self._load_test_dealerships()
        self.test_scenarios = self._load_test_scenarios()
    
    async def run_comprehensive_test(self):
        """Test all strategies against LA area dealerships"""
        
        results = {
            "overall": {"attempted": 0, "successful": 0, "failed": 0},
            "by_strategy": defaultdict(lambda: {"attempted": 0, "successful": 0}),
            "by_dealership": {},
            "error_patterns": defaultdict(int)
        }
        
        for dealership in self.test_dealerships:
            self.logger.info(f"Testing dealership: {dealership['name']}")
            
            test_result = await self._test_dealership(dealership)
            
            results["overall"]["attempted"] += 1
            results["by_dealership"][dealership["id"]] = test_result
            
            if test_result["success"]:
                results["overall"]["successful"] += 1
                results["by_strategy"][test_result["successful_strategy"]]["successful"] += 1
            else:
                results["overall"]["failed"] += 1
                results["error_patterns"][test_result["error_type"]] += 1
        
        # Generate comprehensive report
        return self._generate_test_report(results)
    
    async def _test_dealership(self, dealership):
        """Test autofill on a specific dealership"""
        
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(dealership["website"], timeout=30000)
            
            # Look for contact page
            contact_urls = await self._find_contact_page(page, dealership["website"])
            
            for contact_url in contact_urls:
                await page.goto(contact_url)
                
                # Test autofill
                autofill_engine = CascadingAutofillEngine()
                result = await autofill_engine.fill_dealership_form(
                    page, 
                    dealership, 
                    self._get_test_user_data()
                )
                
                if result.success:
                    return {
                        "success": True,
                        "successful_strategy": result.strategy_used,
                        "contact_url": contact_url,
                        "form_fields_found": result.form_fields_found,
                        "submission_time": result.duration_ms
                    }
            
            return {
                "success": False,
                "error_type": "no_contact_form_found",
                "contact_urls_tried": contact_urls
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        finally:
            await browser.close()
```

## Implementation Priority

1. **Phase 1**: Implement PreMappedStrategy and SemanticFormStrategy
2. **Phase 2**: Add VisualFormStrategy and comprehensive logging
3. **Phase 3**: Integrate Amazon Nova Act and ML components
4. **Phase 4**: Build adaptive learning system
5. **Phase 5**: Deploy comprehensive testing framework

This architecture provides multiple fallback layers, ensuring maximum success rate while maintaining detailed logging for continuous improvement.