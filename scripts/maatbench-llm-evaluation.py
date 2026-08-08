#!/usr/bin/env python3
"""
MaatBench LLM Evaluation - Comprehensive Model Testing
Part of MaatBench benchmarking system for Tehuti Lab
Tests both tool usage AND normal conversation to prevent model damage

This is the LLM Model Evaluation component of MaatBench.
See: docs/MAATBENCH-PLAN.md for the full MaatBench system architecture.

Maat Principles:
- Truth: Honest evaluation of model capabilities (no artificial scores)
- Balance: Test both tool usage and conversation (not just one)
- Order: Systematic testing approach (consistent metrics)
- Justice: Fair evaluation criteria (equal test opportunities)
- Self-Reflection: Learn from test results (improve based on findings)
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field

@dataclass
class TestResult:
    """Individual test result."""
    test_name: str
    category: str  # "tool_usage", "conversation", "balance"
    prompt: str
    expected_behavior: str
    actual_response: str
    score: float  # 0.0 to 1.0
    passed: bool
    notes: str

@dataclass
class BenchmarkReport:
    """Complete benchmark report (aligned with MaatBench structure)."""
    model_name: str
    timestamp: str
    server: str = "local"  # For consistency with MaatBench format
    component: str = "llm_model_evaluation"  # This is the LLM evaluation component
    tool_usage_score: float = 0.0
    conversation_score: float = 0.0
    balance_score: float = 0.0
    overall_score: float = 0.0
    # Performance metrics (aligned with MaatBench)
    latency_ms: float = 0.0  # Average response time
    error_rate: float = 0.0  # Percentage of failures
    # Quality metrics (aligned with MaatBench)
    accuracy: float = 0.0  # Correct results percentage
    precision: float = 0.0  # Relevant results percentage
    recall: float = 0.0  # Coverage percentage
    f1_score: float = 0.0  # Combined accuracy metric
    # Maat compliance metrics (aligned with MaatBench)
    maat_compliance: Dict[str, float] = field(default_factory=dict)
    test_results: List[Dict] = field(default_factory=list)
    summary: str = ""

class MaatBenchLLM:
    """MaatBench for LLM model evaluation."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.test_results: List[TestResult] = []
        
        # Test categories
        self.tool_tests = [
            {
                "name": "list_directory",
                "prompt": "list the files in /home/suspect/.n8n",
                "expected": "should_use_tool",
                "tool": "tool_list_directory_post"
            },
            {
                "name": "read_file",
                "prompt": "read the config.json file",
                "expected": "should_use_tool",
                "tool": "tool_read_file_post"
            },
            {
                "name": "execute_command",
                "prompt": "execute ls -la",
                "expected": "should_use_tool",
                "tool": "tool_execute_command_post"
            },
            {
                "name": "query_gitmaat",
                "prompt": "check gitMaat for pending tasks",
                "expected": "should_use_tool",
                "tool": "tool_query_gitmaat_post"
            },
            {
                "name": "search_n8n_nodes",
                "prompt": "search for HTTP request nodes in n8n",
                "expected": "should_use_tool",
                "tool": "search_nodes"
            }
        ]
        
        self.conversation_tests = [
            {
                "name": "simple_math",
                "prompt": "what's 2+2?",
                "expected": "should_answer_directly",
                "should_not_mention": ["tool", "gitMaat", "query"]
            },
            {
                "name": "general_question",
                "prompt": "what is artificial intelligence?",
                "expected": "should_answer_directly",
                "should_not_mention": ["tool", "gitMaat", "query"]
            },
            {
                "name": "casual_conversation",
                "prompt": "how are you today?",
                "expected": "should_answer_directly",
                "should_not_mention": ["tool", "gitMaat", "query"]
            },
            {
                "name": "explanation_request",
                "prompt": "explain how machine learning works",
                "expected": "should_answer_directly",
                "should_not_mention": ["tool", "gitMaat", "query"]
            },
            {
                "name": "creative_request",
                "prompt": "write a short poem about technology",
                "expected": "should_answer_directly",
                "should_not_mention": ["tool", "gitMaat", "query"]
            }
        ]
        
        self.balance_tests = [
            {
                "name": "tool_when_needed",
                "prompt": "read the file config.json",
                "expected": "should_use_tool",
                "category": "tool_appropriate"
            },
            {
                "name": "no_tool_when_not_needed",
                "prompt": "what's the capital of France?",
                "expected": "should_answer_directly",
                "category": "conversation_appropriate"
            },
            {
                "name": "mixed_scenario",
                "prompt": "I want to start a new task. What should I do first?",
                "expected": "may_use_tool_if_context_needed",
                "category": "judgment_required"
            }
        ]
    
    def run_model(self, prompt: str, timeout: int = 30) -> str:
        """Run model with prompt and return response."""
        try:
            result = subprocess.run(
                ["ollama", "run", self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            # Clean response (remove ANSI codes, thinking markers)
            response = result.stdout
            # Remove common artifacts
            response = response.replace("Thinking...", "").strip()
            # Remove ANSI escape codes
            import re
            response = re.sub(r'\x1b\[[0-9;]*m', '', response)
            return response
        except subprocess.TimeoutExpired:
            return "TIMEOUT: Model took too long to respond"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def test_tool_usage(self) -> List[TestResult]:
        """Test if model uses tools correctly when needed."""
        results = []
        for test in self.tool_tests:
            response = self.run_model(test["prompt"])
            
            # Check if tool is mentioned or used
            tool_mentioned = test["tool"].lower() in response.lower()
            tool_used = f"tool_{test['tool']}" in response.lower() or test["tool"] in response.lower()
            
            # Score: 1.0 if tool used, 0.5 if mentioned, 0.0 if not
            if tool_used:
                score = 1.0
                passed = True
                notes = "Tool correctly used"
            elif tool_mentioned:
                score = 0.5
                passed = False
                notes = "Tool mentioned but not used correctly"
            else:
                score = 0.0
                passed = False
                notes = "Tool not used when it should be"
            
            result = TestResult(
                test_name=test["name"],
                category="tool_usage",
                prompt=test["prompt"],
                expected_behavior=test["expected"],
                actual_response=response[:200],  # First 200 chars
                score=score,
                passed=passed,
                notes=notes
            )
            results.append(result)
        
        return results
    
    def test_conversation(self) -> List[TestResult]:
        """Test if model can have normal conversation without obsessing over tools."""
        results = []
        for test in self.conversation_tests:
            response = self.run_model(test["prompt"])
            
            # Check if model mentions tools when it shouldn't
            tool_obsession = any(
                keyword.lower() in response.lower() 
                for keyword in test.get("should_not_mention", [])
            )
            
            # Check if response is reasonable (not empty, not error)
            is_reasonable = (
                len(response) > 10 and 
                "ERROR" not in response and 
                "TIMEOUT" not in response
            )
            
            # Score: 1.0 if good conversation, 0.0 if tool-obsessed
            if tool_obsession:
                score = 0.0
                passed = False
                notes = f"Model mentioned tools when it shouldn't: {test.get('should_not_mention', [])}"
            elif is_reasonable:
                score = 1.0
                passed = True
                notes = "Good conversational response"
            else:
                score = 0.5
                passed = False
                notes = "Response is too short or contains errors"
            
            result = TestResult(
                test_name=test["name"],
                category="conversation",
                prompt=test["prompt"],
                expected_behavior=test["expected"],
                actual_response=response[:200],
                score=score,
                passed=passed,
                notes=notes
            )
            results.append(result)
        
        return results
    
    def test_balance(self) -> List[TestResult]:
        """Test if model balances tool usage and conversation appropriately."""
        results = []
        for test in self.balance_tests:
            response = self.run_model(test["prompt"])
            
            # For tool-appropriate tests, check if tool is used
            if test["category"] == "tool_appropriate":
                tool_used = any(
                    tool in response.lower() 
                    for tool in ["tool_", "execute", "read", "list", "query"]
                )
                score = 1.0 if tool_used else 0.0
                passed = tool_used
                notes = "Tool used appropriately" if tool_used else "Tool not used when needed"
            
            # For conversation-appropriate tests, check if NO tools mentioned
            elif test["category"] == "conversation_appropriate":
                tool_mentioned = any(
                    keyword in response.lower() 
                    for keyword in ["tool", "gitMaat", "query", "execute"]
                )
                score = 1.0 if not tool_mentioned else 0.0
                passed = not tool_mentioned
                notes = "Direct answer without tools" if not tool_mentioned else "Mentioned tools unnecessarily"
            
            # For judgment tests, either is acceptable
            else:
                has_response = len(response) > 10
                score = 1.0 if has_response else 0.0
                passed = has_response
                notes = "Model made appropriate judgment"
            
            result = TestResult(
                test_name=test["name"],
                category="balance",
                prompt=test["prompt"],
                expected_behavior=test["expected"],
                actual_response=response[:200],
                score=score,
                passed=passed,
                notes=notes
            )
            results.append(result)
        
        return results
    
    def run_all_tests(self) -> BenchmarkReport:
        """Run all tests and generate report."""
        print(f"🧪 Running MaatBench for {self.model_name}...")
        print("=" * 60)
        
        # Run tests
        print("\n1. Testing Tool Usage...")
        tool_results = self.test_tool_usage()
        self.test_results.extend(tool_results)
        
        print("\n2. Testing Normal Conversation...")
        conversation_results = self.test_conversation()
        self.test_results.extend(conversation_results)
        
        print("\n3. Testing Balance...")
        balance_results = self.test_balance()
        self.test_results.extend(balance_results)
        
        # Calculate scores
        tool_score = sum(r.score for r in tool_results) / len(tool_results) if tool_results else 0.0
        conversation_score = sum(r.score for r in conversation_results) / len(conversation_results) if conversation_results else 0.0
        balance_score = sum(r.score for r in balance_results) / len(balance_results) if balance_results else 0.0
        
        # Overall score: average of all three
        overall_score = (tool_score + conversation_score + balance_score) / 3.0
        
        # Calculate performance metrics
        all_responses = [r.actual_response for r in self.test_results]
        avg_latency = 0.0  # Would need timing data
        error_count = sum(1 for r in self.test_results if "ERROR" in r.actual_response or "TIMEOUT" in r.actual_response)
        error_rate = error_count / len(self.test_results) if self.test_results else 0.0
        
        # Calculate quality metrics
        accuracy = overall_score  # Overall score is our accuracy metric
        precision = tool_score  # Tool usage precision
        recall = conversation_score  # Conversation recall (coverage)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Calculate Maat compliance (aligned with MaatBench format)
        maat_compliance = {
            "truth": 1.0 if error_rate < 0.1 else 0.5,  # Honest reporting
            "balance": balance_score,  # Balanced tool/conversation usage
            "order": 1.0 if overall_score > 0.7 else 0.5,  # Consistent performance
            "justice": 1.0 if tool_score > 0.5 and conversation_score > 0.5 else 0.5,  # Fair evaluation
            "self_reflection": 1.0 if overall_score > 0.6 else 0.0  # Learning capability
        }
        
        # Generate summary
        summary = f"""
MaatBench Results for {self.model_name}

Tool Usage Score: {tool_score:.2%} ({sum(1 for r in tool_results if r.passed)}/{len(tool_results)} passed)
Conversation Score: {conversation_score:.2%} ({sum(1 for r in conversation_results if r.passed)}/{len(conversation_results)} passed)
Balance Score: {balance_score:.2%} ({sum(1 for r in balance_results if r.passed)}/{len(balance_results)} passed)

Overall Score: {overall_score:.2%}

Interpretation:
- Tool Usage: Can the model use tools when needed?
- Conversation: Can the model have normal conversations without tool obsession?
- Balance: Does the model balance both appropriately?

⚠️  WARNING: If conversation_score < 0.5, the model may be tool-obsessed and damaged.
✅ GOOD: If all scores > 0.7, the model is well-balanced.
"""
        
        # Create report (aligned with MaatBench format)
        report = BenchmarkReport(
            model_name=self.model_name,
            timestamp=datetime.now().isoformat(),
            server="local",
            component="llm_model_evaluation",
            tool_usage_score=tool_score,
            conversation_score=conversation_score,
            balance_score=balance_score,
            overall_score=overall_score,
            latency_ms=avg_latency,
            error_rate=error_rate,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            maat_compliance=maat_compliance,
            test_results=[asdict(r) for r in self.test_results],
            summary=summary
        )
        
        return report
    
    def save_report(self, report: BenchmarkReport, output_file: str):
        """Save report to JSON file and log to gitMaat."""
        report_dict = asdict(report)
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
        print(f"\n📊 Report saved to: {output_file}")
        
        # Log to gitMaat for tracking
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "maatlangchain"))
            from maat_memory import MaatMemory, get_unique_agent_id
            
            memory = MaatMemory()
            agent_id = get_unique_agent_id("maatbench")
            
            # Log as a learning (benchmark insights)
            memory.log_learning(
                agent_id=agent_id,
                topic=f"MaatBench LLM Evaluation: {self.model_name}",
                insight=f"Tool Usage: {report.tool_usage_score:.2%}, Conversation: {report.conversation_score:.2%}, Balance: {report.balance_score:.2%}, Overall: {report.overall_score:.2%}",
                source="maatbench-llm-evaluation.py",
                confidence=1.0 if report.overall_score > 0.7 else 0.5
            )
            
            # Log as a change (benchmark run)
            memory.log_change(
                agent_id=agent_id,
                file_path=output_file,
                change_type="create",
                summary=f"MaatBench LLM evaluation for {self.model_name}",
                reason=f"Benchmark run: Overall score {report.overall_score:.2%}"
            )
            
            print(f"✅ Results logged to gitMaat")
        except Exception as e:
            print(f"⚠️  Could not log to gitMaat: {e}")
            print("   (Report still saved to file)")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 maatbench-llm-evaluation.py <model_name>")
        print("Example: python3 maatbench-llm-evaluation.py tehuti-lab:llama3.1-8b-maat")
        sys.exit(1)
    
    model_name = sys.argv[1]
    benchmark = MaatBenchLLM(model_name)
    
    # Run tests
    report = benchmark.run_all_tests()
    
    # Print summary
    print(report.summary)
    
    # Save report
    output_file = f"/tmp/maatbench-{model_name.replace(':', '-')}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    benchmark.save_report(report, output_file)
    
    # Exit code based on overall score
    if report.overall_score >= 0.7:
        print("\n✅ Model passed MaatBench (score >= 70%)")
        sys.exit(0)
    elif report.conversation_score < 0.5:
        print("\n❌ Model FAILED: Tool-obsessed (conversation score < 50%)")
        sys.exit(1)
    else:
        print("\n⚠️  Model needs improvement (score < 70%)")
        sys.exit(1)

if __name__ == "__main__":
    main()

