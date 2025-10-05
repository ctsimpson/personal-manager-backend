def _configure_proxy_bypass():
        """Configure environment to bypass proxy for Hugging Face"""
        import os
        
        # Set no_proxy environment variable
        current_no_proxy = os.environ.get('no_proxy', '')
        huggingface_domains = 'huggingface.co,cdn-lfs.huggingface.co,cdn-lfs-us-1.huggingface.co'
        
        if current_no_proxy:
            os.environ['no_proxy'] = f"{current_no_proxy},{huggingface_domains}"
        else:
            os.environ['no_proxy'] = huggingface_domains
        
        # Also set NO_PROXY (some systems use this instead)
        os.environ['NO_PROXY'] = os.environ['no_proxy']
        
        print(f"Set no_proxy to: {os.environ['no_proxy']}")