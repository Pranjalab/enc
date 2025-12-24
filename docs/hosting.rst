Hosting the Documentation
=========================

This documentation is built using **Sphinx**. You can host it on any static site provider (GitHub Pages, Netlify, Vercel) or run it locally.

Building Locally
----------------

To generate the HTML files from the source:

1.  **Install Requirements**:

    .. code-block:: bash

        pip install sphinx sphinx_rtd_theme

2.  **Run Build**:

    .. code-block:: bash

        cd docs
        make html

3.  **View**:
    Open ``docs/_build/html/index.html`` in your browser.

Deploying to GitHub Pages
-------------------------

We have configured an automated GitHub Actions workflow to publish these docs.

1.  **Workflow File**: Included at ``.github/workflows/deploy-docs.yml``.
2.  **Trigger**: Pushes to the ``main`` branch.

Configuration Steps
~~~~~~~~~~~~~~~~~~~

To enable this on your fork:

1.  Go to your repository **Settings** > **Pages**.
2.  Under **Build and deployment** > **Source**, keep it as "Deploy from a branch".
3.  **Important**: The workflow pushes to a branch named ``gh-pages``.
    *   Wait for the first Action run to complete (it will create the branch).
    *   Then, in Settings > Pages, select ``gh-pages`` as the **Branch** and ``/ (root)`` as the folder.
    *   Click **Save**.

Your docs will be live at ``https://<username>.github.io/enc/``.

.. note::
   GitHub Pages and GitHub Actions are **free** for public repositories. No payment or billing setup is required.
