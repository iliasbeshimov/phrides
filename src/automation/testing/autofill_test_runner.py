"""
Comprehensive test framework for autofill strategies.
Tests all strategies against LA area dealerships with detailed reporting.
"""

import asyncio
import csv
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import traceback
from playwright.async_api import async_playwright, Browser, Page

from ..forms.form_detector import (
    PreMappedFormStrategy, 
    SemanticFormStrategy,
    FormDetectionResult
)
from ..nova_act.nova_integration import NovaActClient
from ...core.models.contact_request import ContactRequest, UserInfo
from ...utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TestDealership:
    """Test dealership data"""
    id: str
    name: str
    website: str
    city: str
    state: str
    phone: str
    expected_contact_pages: List[str] = None


@dataclass
class StrategyTestResult:
    """Result of testing a single strategy on a dealership"""
    strategy_name: str
    success: bool
    confidence_score: float
    fields_detected: List[str]
    form_submitted: bool
    error_message: Optional[str]
    duration_seconds: float
    screenshots: List[str]
    metadata: Dict[str, Any]


@dataclass
class DealershipTestResult:
    """Complete test result for a dealership"""
    dealership_id: str
    dealership_name: str
    website: str
    contact_pages_found: List[str]
    strategy_results: List[StrategyTestResult]
    successful_strategy: Optional[str]
    overall_success: bool
    total_time_seconds: float
    final_status: str
    error_summary: List[str]


@dataclass
class TestSuiteResult:
    """Overall test suite results"""
    total_dealerships: int
    successful_dealerships: int
    failed_dealerships: int
    success_rate: float
    strategy_performance: Dict[str, Dict[str, Any]]
    common_failures: Dict[str, int]
    performance_metrics: Dict[str, float]
    detailed_results: List[DealershipTestResult]
    execution_time_seconds: float


class AutofillTestRunner:
    """Main test runner for autofill strategies"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.test_dealerships = self._load_test_dealerships()
        self.test_user_data = self._create_test_user_data()
        self.strategies = self._initialize_strategies()
        self.logger = logger
        
        # Create results directory
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load test configuration"""
        default_config = {
            "browser_config": {
                "headless": True,
                "viewport": {"width": 1920, "height": 1080},
                "timeout": 30000
            },
            "test_config": {
                "max_strategies_per_dealership": 5,
                "timeout_per_strategy": 60,
                "screenshot_on_failure": True,
                "retry_failed_tests": False
            },
            "contact_page_patterns": [
                "/contact", "/contact-us", "/inquiry", "/quote", 
                "/get-quote", "/contact-dealer", "/sales"
            ]
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _load_test_dealerships(self) -> List[TestDealership]:
        """Load test dealerships from CSV"""
        dealerships = []
        csv_path = Path("data/test_dealerships_la.csv")
        
        if csv_path.exists():
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dealership = TestDealership(
                        id=row['dealer_code'],
                        name=row['dealer_name'],
                        website=row['website'] if row['website'] else None,
                        city=row['city'],
                        state=row['state'],
                        phone=row['phone']
                    )
                    if dealership.website:  # Only test dealerships with websites
                        dealerships.append(dealership)
        
        return dealerships
    
    def _create_test_user_data(self) -> ContactRequest:
        """Create test user data for form filling"""
        user_info = UserInfo(
            first_name="John",
            last_name="TestUser", 
            email="john.testuser@example.com",
            phone="(555) 123-4567",
            preferred_contact_method="email"
        )
        
        return ContactRequest(
            user_info=user_info,
            custom_message="I'm interested in learning more about your Jeep inventory. Please contact me with available models and pricing information.",
            vehicle_preferences=["Jeep"]
        )
    
    def _initialize_strategies(self) -> List:
        """Initialize all autofill strategies"""
        strategies = [
            PreMappedFormStrategy(),
            SemanticFormStrategy()
        ]
        
        # Add Nova Act if configured
        if self.config.get("enable_nova_act", False):
            strategies.append(NovaActClient())
        
        return strategies
    
    async def run_comprehensive_test(self) -> TestSuiteResult:
        """Run comprehensive test suite across all dealerships"""
        
        start_time = datetime.now()
        
        self.logger.info("Starting comprehensive autofill test suite", {
            "operation": "test_suite_start",
            "total_dealerships": len(self.test_dealerships),
            "strategies_count": len(self.strategies),
            "test_user": self.test_user_data.user_info.email
        })
        
        detailed_results = []
        successful_count = 0
        failed_count = 0
        strategy_stats = {strategy.__class__.__name__: {"attempts": 0, "successes": 0} 
                         for strategy in self.strategies}
        common_failures = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(**self.config["browser_config"])
            
            try:
                for i, dealership in enumerate(self.test_dealerships, 1):
                    self.logger.info(f"Testing dealership {i}/{len(self.test_dealerships)}", {
                        "operation": "dealership_test_start",
                        "dealership_id": dealership.id,
                        "dealership_name": dealership.name,
                        "website": dealership.website
                    })
                    
                    try:
                        result = await self._test_dealership(browser, dealership)
                        detailed_results.append(result)
                        
                        if result.overall_success:
                            successful_count += 1
                        else:
                            failed_count += 1
                            
                        # Update strategy statistics
                        for strategy_result in result.strategy_results:
                            strategy_name = strategy_result.strategy_name
                            if strategy_name in strategy_stats:
                                strategy_stats[strategy_name]["attempts"] += 1
                                if strategy_result.success:
                                    strategy_stats[strategy_name]["successes"] += 1
                        
                        # Track common failure patterns
                        if not result.overall_success:
                            for error in result.error_summary:
                                common_failures[error] = common_failures.get(error, 0) + 1
                                
                    except Exception as e:
                        self.logger.error("Dealership test failed", {
                            "operation": "dealership_test_error",
                            "dealership_id": dealership.id,
                            "error": str(e)
                        })
                        
                        failed_result = DealershipTestResult(
                            dealership_id=dealership.id,
                            dealership_name=dealership.name,
                            website=dealership.website,
                            contact_pages_found=[],
                            strategy_results=[],
                            successful_strategy=None,
                            overall_success=False,
                            total_time_seconds=0,
                            final_status="test_error",
                            error_summary=[f"Test execution error: {str(e)}"]
                        )
                        detailed_results.append(failed_result)
                        failed_count += 1
            
            finally:
                await browser.close()
        
        # Calculate final metrics
        total_time = (datetime.now() - start_time).total_seconds()
        success_rate = (successful_count / len(self.test_dealerships)) * 100 if self.test_dealerships else 0
        
        # Calculate strategy performance
        strategy_performance = {}
        for strategy_name, stats in strategy_stats.items():
            success_rate_strategy = (stats["successes"] / stats["attempts"] * 100) if stats["attempts"] > 0 else 0
            strategy_performance[strategy_name] = {
                "attempts": stats["attempts"],
                "successes": stats["successes"],
                "success_rate": success_rate_strategy,
                "avg_time": self._calculate_avg_strategy_time(detailed_results, strategy_name)
            }
        
        # Performance metrics
        performance_metrics = {
            "avg_time_per_dealership": total_time / len(self.test_dealerships) if self.test_dealerships else 0,
            "total_forms_detected": sum(len(r.strategy_results) for r in detailed_results),
            "total_successful_submissions": sum(1 for r in detailed_results if r.overall_success)
        }
        
        result = TestSuiteResult(
            total_dealerships=len(self.test_dealerships),
            successful_dealerships=successful_count,
            failed_dealerships=failed_count,
            success_rate=success_rate,
            strategy_performance=strategy_performance,
            common_failures=common_failures,
            performance_metrics=performance_metrics,
            detailed_results=detailed_results,
            execution_time_seconds=total_time
        )
        
        # Save results
        await self._save_test_results(result)
        
        self.logger.info("Test suite completed", {
            "operation": "test_suite_complete",
            "success_rate": success_rate,
            "successful_dealerships": successful_count,
            "failed_dealerships": failed_count,
            "execution_time": total_time
        })
        
        return result
    
    async def _test_dealership(self, browser: Browser, dealership: TestDealership) -> DealershipTestResult:
        """Test autofill strategies on a single dealership"""
        
        start_time = datetime.now()
        strategy_results = []
        contact_pages = []
        successful_strategy = None
        
        page = await browser.new_page()
        
        try:
            # Find contact pages
            contact_pages = await self._find_contact_pages(page, dealership)
            
            if not contact_pages:
                return DealershipTestResult(
                    dealership_id=dealership.id,
                    dealership_name=dealership.name,
                    website=dealership.website,
                    contact_pages_found=[],
                    strategy_results=[],
                    successful_strategy=None,
                    overall_success=False,
                    total_time_seconds=(datetime.now() - start_time).total_seconds(),
                    final_status="no_contact_pages",
                    error_summary=["No contact pages found"]
                )
            
            # Test strategies on each contact page
            for contact_url in contact_pages:
                await page.goto(contact_url, timeout=self.config["browser_config"]["timeout"])
                
                for strategy in self.strategies:
                    strategy_start_time = datetime.now()
                    
                    try:
                        result = await self._test_strategy_on_page(page, strategy, dealership)
                        strategy_results.append(result)
                        
                        if result.success and not successful_strategy:
                            successful_strategy = result.strategy_name
                            
                    except Exception as e:
                        error_result = StrategyTestResult(
                            strategy_name=strategy.__class__.__name__,
                            success=False,
                            confidence_score=0.0,
                            fields_detected=[],
                            form_submitted=False,
                            error_message=str(e),
                            duration_seconds=(datetime.now() - strategy_start_time).total_seconds(),
                            screenshots=[],
                            metadata={"error": str(e)}
                        )
                        strategy_results.append(error_result)
                
                # If we found a successful strategy, we can stop testing
                if successful_strategy:
                    break
        
        finally:
            await page.close()
        
        total_time = (datetime.now() - start_time).total_seconds()
        overall_success = successful_strategy is not None
        
        # Determine final status
        if overall_success:
            final_status = "success"
        elif not contact_pages:
            final_status = "no_contact_pages"
        elif not strategy_results:
            final_status = "no_strategies_tested"
        else:
            final_status = "all_strategies_failed"
        
        # Collect error summary
        error_summary = []
        if not overall_success:
            for result in strategy_results:
                if result.error_message:
                    error_summary.append(f"{result.strategy_name}: {result.error_message}")
        
        return DealershipTestResult(
            dealership_id=dealership.id,
            dealership_name=dealership.name,
            website=dealership.website,
            contact_pages_found=contact_pages,
            strategy_results=strategy_results,
            successful_strategy=successful_strategy,
            overall_success=overall_success,
            total_time_seconds=total_time,
            final_status=final_status,
            error_summary=error_summary
        )
    
    async def _find_contact_pages(self, page: Page, dealership: TestDealership) -> List[str]:
        """Find contact pages for the dealership"""
        
        contact_pages = []
        base_url = dealership.website
        
        if not base_url:
            return []
        
        try:
            # Start with the main page
            await page.goto(base_url, timeout=self.config["browser_config"]["timeout"])
            
            # Check if the main page has a contact form
            if await self._has_contact_form(page):
                contact_pages.append(page.url)
            
            # Look for contact page links
            contact_link_selectors = [
                "a[href*='contact']",
                "a[href*='inquiry']", 
                "a[href*='quote']",
                "a[href*='sales']",
                "a:contains('Contact')",
                "a:contains('Get Quote')",
                "a:contains('Inquiry')"
            ]
            
            for selector in contact_link_selectors:
                try:
                    links = page.locator(selector)
                    count = await links.count()
                    
                    for i in range(min(count, 3)):  # Limit to first 3 matches
                        link = links.nth(i)
                        href = await link.get_attribute("href")
                        
                        if href:
                            # Convert relative URLs to absolute
                            if href.startswith("/"):
                                full_url = f"{base_url.rstrip('/')}{href}"
                            elif href.startswith("http"):
                                full_url = href
                            else:
                                full_url = f"{base_url.rstrip('/')}/{href}"
                            
                            if full_url not in contact_pages:
                                # Test if this page has a contact form
                                try:
                                    await page.goto(full_url, timeout=15000)
                                    if await self._has_contact_form(page):
                                        contact_pages.append(full_url)
                                except Exception:
                                    continue  # Skip problematic URLs
                                
                except Exception:
                    continue  # Skip problematic selectors
            
            # Try common contact page URLs
            common_paths = self.config["contact_page_patterns"]
            for path in common_paths:
                try:
                    test_url = f"{base_url.rstrip('/')}{path}"
                    await page.goto(test_url, timeout=15000)
                    
                    # Check if page loaded successfully and has a form
                    if page.url != test_url and "404" not in await page.title():
                        continue
                        
                    if await self._has_contact_form(page):
                        if test_url not in contact_pages:
                            contact_pages.append(test_url)
                            
                except Exception:
                    continue  # Skip URLs that don't exist
        
        except Exception as e:
            self.logger.warning("Error finding contact pages", {
                "operation": "find_contact_pages_error",
                "dealership_id": dealership.id,
                "error": str(e)
            })
        
        return contact_pages[:3]  # Limit to 3 contact pages max
    
    async def _has_contact_form(self, page: Page) -> bool:
        """Check if page has a contact form"""
        
        try:
            # Look for form elements
            forms = page.locator("form")
            form_count = await forms.count()
            
            if form_count == 0:
                return False
            
            # Check if any form looks like a contact form
            for i in range(form_count):
                form = forms.nth(i)
                form_html = await form.inner_html()
                form_text = await form.inner_text() if form_html else ""
                
                # Look for contact-like fields
                contact_indicators = [
                    'type="email"', 'name="email"', 'name="phone"',
                    'name="first', 'name="last', 'textarea',
                    'contact', 'inquiry', 'message'
                ]
                
                combined_content = f"{form_html} {form_text}".lower()
                
                if any(indicator in combined_content for indicator in contact_indicators):
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _test_strategy_on_page(self, page: Page, strategy, dealership: TestDealership) -> StrategyTestResult:
        """Test a single strategy on the current page"""
        
        start_time = datetime.now()
        screenshots = []
        
        try:
            # Take initial screenshot
            if self.config["test_config"]["screenshot_on_failure"]:
                initial_screenshot = await page.screenshot()
                screenshots.append(f"initial_{strategy.__class__.__name__}.png")
            
            if hasattr(strategy, 'detect_form'):
                # Form detection strategy
                result = await strategy.detect_form(page)
                
                if result.success:
                    # Try to fill the form
                    form_filled = await self._fill_detected_form(page, result, self.test_user_data)
                    
                    return StrategyTestResult(
                        strategy_name=strategy.__class__.__name__,
                        success=form_filled,
                        confidence_score=result.confidence_score,
                        fields_detected=list(result.fields.keys()),
                        form_submitted=form_filled,
                        error_message=None,
                        duration_seconds=(datetime.now() - start_time).total_seconds(),
                        screenshots=screenshots,
                        metadata={
                            "detection_strategy": result.detection_strategy,
                            "form_element_found": result.form_element is not None,
                            "submit_button_found": result.submit_button is not None
                        }
                    )
                else:
                    return StrategyTestResult(
                        strategy_name=strategy.__class__.__name__,
                        success=False,
                        confidence_score=result.confidence_score,
                        fields_detected=[],
                        form_submitted=False,
                        error_message=result.metadata.get("reason", "Form detection failed"),
                        duration_seconds=(datetime.now() - start_time).total_seconds(),
                        screenshots=screenshots,
                        metadata=result.metadata
                    )
            
            elif hasattr(strategy, 'execute_form_filling_task'):
                # Nova Act strategy
                result = await strategy.execute_form_filling_task(page, self.test_user_data)
                
                return StrategyTestResult(
                    strategy_name=strategy.__class__.__name__,
                    success=result.success,
                    confidence_score=1.0 if result.success else 0.0,
                    fields_detected=["nova_act_handled"],
                    form_submitted=result.form_submitted,
                    error_message="; ".join(result.errors) if result.errors else None,
                    duration_seconds=result.duration_seconds,
                    screenshots=result.screenshots[:3],  # Limit screenshots
                    metadata={
                        "steps_taken": len(result.steps_taken),
                        "final_state": result.final_state,
                        "confirmation_detected": result.confirmation_detected
                    }
                )
            
            else:
                return StrategyTestResult(
                    strategy_name=strategy.__class__.__name__,
                    success=False,
                    confidence_score=0.0,
                    fields_detected=[],
                    form_submitted=False,
                    error_message="Unknown strategy type",
                    duration_seconds=(datetime.now() - start_time).total_seconds(),
                    screenshots=screenshots,
                    metadata={"error": "Unknown strategy interface"}
                )
                
        except Exception as e:
            return StrategyTestResult(
                strategy_name=strategy.__class__.__name__,
                success=False,
                confidence_score=0.0,
                fields_detected=[],
                form_submitted=False,
                error_message=str(e),
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                screenshots=screenshots,
                metadata={"exception": str(e), "traceback": traceback.format_exc()}
            )
    
    async def _fill_detected_form(self, page: Page, form_result: FormDetectionResult, user_data: ContactRequest) -> bool:
        """Fill a detected form with user data"""
        
        try:
            # Fill form fields
            fields_filled = 0
            
            for field_type, field_info in form_result.fields.items():
                try:
                    if field_type == "first_name":
                        await field_info.element.fill(user_data.user_info.first_name)
                        fields_filled += 1
                    elif field_type == "last_name":
                        await field_info.element.fill(user_data.user_info.last_name)
                        fields_filled += 1
                    elif field_type == "email":
                        await field_info.element.fill(user_data.user_info.email)
                        fields_filled += 1
                    elif field_type == "phone":
                        await field_info.element.fill(user_data.user_info.phone)
                        fields_filled += 1
                    elif field_type == "message":
                        await field_info.element.fill(user_data.custom_message)
                        fields_filled += 1
                    elif field_type == "vehicle_interest":
                        # Try to select Jeep from dropdown
                        try:
                            await field_info.element.select_option(label="Jeep")
                            fields_filled += 1
                        except:
                            try:
                                await field_info.element.select_option(value="jeep")
                                fields_filled += 1
                            except:
                                pass  # Skip if can't select Jeep option
                                
                except Exception as e:
                    self.logger.debug(f"Failed to fill field {field_type}: {str(e)}")
                    continue
            
            # Only submit if we filled at least 2 fields
            if fields_filled >= 2 and form_result.submit_button:
                try:
                    await form_result.submit_button.click()
                    
                    # Wait for potential response
                    await page.wait_for_timeout(3000)
                    
                    return True
                except Exception as e:
                    self.logger.debug(f"Form submission failed: {str(e)}")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Form filling failed: {str(e)}")
            return False
    
    def _calculate_avg_strategy_time(self, results: List[DealershipTestResult], strategy_name: str) -> float:
        """Calculate average execution time for a strategy"""
        
        times = []
        for result in results:
            for strategy_result in result.strategy_results:
                if strategy_result.strategy_name == strategy_name:
                    times.append(strategy_result.duration_seconds)
        
        return sum(times) / len(times) if times else 0.0
    
    async def _save_test_results(self, results: TestSuiteResult):
        """Save test results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_path = self.results_dir / f"test_results_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(asdict(results), f, indent=2, default=str)
        
        # Save CSV summary
        csv_path = self.results_dir / f"test_summary_{timestamp}.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Dealership ID", "Dealership Name", "Website", 
                "Success", "Successful Strategy", "Contact Pages Found",
                "Total Time", "Error Summary"
            ])
            
            for result in results.detailed_results:
                writer.writerow([
                    result.dealership_id,
                    result.dealership_name,
                    result.website,
                    result.overall_success,
                    result.successful_strategy or "None",
                    "; ".join(result.contact_pages_found),
                    f"{result.total_time_seconds:.2f}s",
                    "; ".join(result.error_summary)
                ])
        
        # Save detailed report
        report_path = self.results_dir / f"test_report_{timestamp}.txt"
        with open(report_path, 'w') as f:
            f.write(self._generate_text_report(results))
        
        self.logger.info("Test results saved", {
            "operation": "test_results_saved",
            "json_path": str(json_path),
            "csv_path": str(csv_path),
            "report_path": str(report_path)
        })
    
    def _generate_text_report(self, results: TestSuiteResult) -> str:
        """Generate a human-readable text report"""
        
        report = f"""
AUTOFILL TEST SUITE RESULTS
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
============================================

OVERALL SUMMARY:
- Total Dealerships Tested: {results.total_dealerships}
- Successful: {results.successful_dealerships}
- Failed: {results.failed_dealerships}
- Success Rate: {results.success_rate:.1f}%
- Total Execution Time: {results.execution_time_seconds:.2f} seconds

STRATEGY PERFORMANCE:
"""
        
        for strategy, perf in results.strategy_performance.items():
            report += f"- {strategy}:\n"
            report += f"  * Attempts: {perf['attempts']}\n"
            report += f"  * Successes: {perf['successes']}\n"
            report += f"  * Success Rate: {perf['success_rate']:.1f}%\n"
            report += f"  * Avg Time: {perf['avg_time']:.2f}s\n\n"
        
        report += "\nCOMMON FAILURE PATTERNS:\n"
        for error, count in sorted(results.common_failures.items(), key=lambda x: x[1], reverse=True):
            report += f"- {error}: {count} occurrences\n"
        
        report += "\nDETAILED RESULTS BY DEALERSHIP:\n"
        for result in results.detailed_results:
            report += f"\n{result.dealership_name} ({result.dealership_id}):\n"
            report += f"  Website: {result.website}\n"
            report += f"  Success: {result.overall_success}\n"
            report += f"  Successful Strategy: {result.successful_strategy or 'None'}\n"
            report += f"  Contact Pages: {len(result.contact_pages_found)}\n"
            report += f"  Time: {result.total_time_seconds:.2f}s\n"
            
            if result.error_summary:
                report += f"  Errors: {'; '.join(result.error_summary)}\n"
        
        return report


# Test execution script
async def main():
    """Main test execution function"""
    
    test_runner = AutofillTestRunner()
    results = await test_runner.run_comprehensive_test()
    
    print(f"\nTest Suite Completed!")
    print(f"Success Rate: {results.success_rate:.1f}%")
    print(f"Successful: {results.successful_dealerships}/{results.total_dealerships}")
    print(f"Execution Time: {results.execution_time_seconds:.2f} seconds")
    
    # Print strategy performance
    print("\nStrategy Performance:")
    for strategy, perf in results.strategy_performance.items():
        print(f"  {strategy}: {perf['success_rate']:.1f}% ({perf['successes']}/{perf['attempts']})")


if __name__ == "__main__":
    asyncio.run(main())