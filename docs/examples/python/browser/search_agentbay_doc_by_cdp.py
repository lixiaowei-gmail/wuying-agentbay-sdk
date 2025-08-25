"""
Example demonstrating AIBrowser capabilites with AgentBay SDK.
This example shows how to use AIBrowser to visit aliyun.com, including:
- Create AIBrowser session
- Use cdp-use to connect to AIBrowser instance through CDP protocol
- Utilize cdp-use to visit aliyun.com
"""

import os
import time
import asyncio

from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption

# Import cdp-use client
from cdp_use import CDPClient

async def main():
    # Get API key from environment variable
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    # Initialize AgentBay client
    print("Initializing AgentBay client...")
    agent_bay = AgentBay(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    params = CreateSessionParams(
        image_id="browser_latest",  # Specify the image ID
    )
    session_result = agent_bay.create(params)

    if session_result.success:
        session = session_result.session
        print(f"Session created with ID: {session.session_id}")

        if await session.browser.initialize_async(BrowserOption()):
            print("Browser initialized successfully")
            endpoint_url = session.browser.get_endpoint_url()
            print("endpoint_url =", endpoint_url)

            # Create and start CDP client
            cdp_client = CDPClient(endpoint_url)
            await cdp_client.start()
            print("CDP client started successfully")

            # Create a new page target
            create_target_result = await cdp_client.send.Target.createTarget(
                params={
                    'url': 'about:blank'
                }
            )
            target_id = create_target_result['targetId']
            print(f"Created new target with ID: {target_id}")

            # Attach to the target
            attach_result = await cdp_client.send.Target.attachToTarget(
                params={
                    'targetId': target_id,
                    'flatten': True
                }
            )
            session_id = attach_result['sessionId']
            print(f"Attached to target with session ID: {session_id}")

            # Enable necessary domains
            await cdp_client.send.Page.enable(session_id=session_id)
            await cdp_client.send.Network.enable(session_id=session_id)
            await cdp_client.send.Runtime.enable(session_id=session_id)

            # Navigate to aliyun.com
            await cdp_client.send.Page.navigate(
                params={
                    'url': 'https://www.aliyun.com'
                },
                session_id=session_id
            )
            print("Navigated to https://www.aliyun.com")

            # Wait for page to load
            await asyncio.sleep(10)

            # Find the search input field and enter search term
            search_expr_result = await cdp_client.send.Runtime.evaluate(
                params={
                     'expression': """document.querySelector("input[class*='search-input']")"""
                },
                session_id=session_id
            )
            print("Search expr result: ", search_expr_result)
            
            if 'exceptionDetails' not in search_expr_result:
                # Focus on the search input
                await cdp_client.send.Runtime.evaluate(
                    params={
                        'expression': """document.querySelector("input[class*='search-input']").focus()"""
                    },
                    session_id=session_id
                )
                
                # Enter search text
                await cdp_client.send.Input.insertText(
                    params={
                        'text': 'Agentbay帮助文档'
                    },
                    session_id=session_id
                )
                print("Entered search text: Agentbay帮助文档")
                
                # Press Enter key
                await cdp_client.send.Input.dispatchKeyEvent(
                    params={
                        'type': 'keyDown',
                        'key': 'Enter',
                        'code': 'Enter',
                        'nativeVirtualKeyCode': 13,
                        'windowsVirtualKeyCode': 13
                    },
                    session_id=session_id
                )
                await cdp_client.send.Input.dispatchKeyEvent(
                    params={
                        'type': 'keyUp',
                        'key': 'Enter',
                        'code': 'Enter',
                        'nativeVirtualKeyCode': 13,
                        'windowsVirtualKeyCode': 13
                    },
                    session_id=session_id
                )
                print("Pressed Enter key")
                
                # Wait for search results
                await asyncio.sleep(10)
                
                # Find link containing "无影AgentBay"
                wuying_link_expr = '''
                (() => {
                    const links = Array.from(document.querySelectorAll("a[class*='search-result-title']"));
                    const targetLink = links.find(link => link.textContent.includes('无影AgentBay'));
                    if (targetLink) {
                        console.log(targetLink);
                        targetLink.click();
                        setTimeout(() => {
                            console.log("click done for element:", targetLink);
                        }, 1000);
                        return true;
                    }
                    return false;
                })()
                '''
                
                wuying_link_result = await cdp_client.send.Runtime.evaluate(
                    params={
                        'expression': wuying_link_expr,
                        'returnByValue': True
                    },
                    session_id=session_id
                )
                
                if 'exceptionDetails' not in wuying_link_result and 'result' in wuying_link_result:
                    result_data = wuying_link_result['result']
                    if 'value' in result_data and result_data['value']:
                        print("Clicked link containing '无影AgentBay'")
                        
                        # Wait for page to load
                        await asyncio.sleep(5)
                        
                        # Find link containing "document_detail"
                        doc_link_expr = '''
                        (() => {
                            const links = Array.from(document.querySelectorAll('a'));
                            const targetLink = links.find(link => link.href.includes('document_detail'));
                            console.log(targetLink);
                            if (targetLink) {
                                targetLink.click();
                                setTimeout(() => {
                                    console.log("=== Click click completed ===");
                                }, 1000);
                                return true;
                            }
                            return false;
                        })()
                        '''
                        
                        doc_link_result = await cdp_client.send.Runtime.evaluate(
                            params={
                                'expression': doc_link_expr,
                                'returnByValue': True
                            },
                            session_id=session_id
                        )
                        
                        if 'exceptionDetails' not in doc_link_result and 'result' in doc_link_result:
                            doc_result_data = doc_link_result['result']
                            if 'value' in doc_result_data and doc_result_data['value']:
                                print("Clicked link containing 'document_detail'")
                                print("Successfully navigated to the target page")
                                
                                # Wait for navigation and observe the result
                                await asyncio.sleep(10)
                                print("Task completed successfully")
                            else:
                                print("Could not find link containing 'document_detail'")
                        else:
                            print("Error finding document link")
                    else:
                        print("Could not find link containing '无影AgentBay'")
                else:
                    print("Error finding wuying link")
            else:
                print("Search input field not found")

            # Cleanup
            await cdp_client.stop()
            print("CDP client stopped")
        else:
            print("Failed to initialize browser")
    else:
        print(f"Failed to create session: {session_result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())