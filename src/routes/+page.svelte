<script>
  import { page } from "$app/state";
	import * as XLSX from 'xlsx';
  import { TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell, TableSearch, Dropdown, DropdownItem, Checkbox, ButtonGroup, List, Li, FloatingLabelInput} from 'flowbite-svelte';
	import { Drawer, Button, CloseButton, Label, Input, Textarea, Select } from 'flowbite-svelte';
	import { Section } from 'flowbite-svelte-blocks';
	import { PlusOutline, ChevronDownOutline, FilterSolid, ChevronRightOutline, ChevronLeftOutline, QrCodeOutline} from 'flowbite-svelte-icons';

  const { user } = $props();

  /* ------------------  Main Table function ----------------------- */

	let divClass = 'bg-white dark:bg-gray-800 relative shadow-md sm:rounded-lg overflow-hidden';
	let innerDivClass = 'flex flex-col md:flex-row items-center justify-between space-y-3 md:space-y-0 md:space-x-4 p-4';
	let searchClass = 'w-full md:w-1/2 relative';

	let searchTerm = $state('');
	let currentPosition = $state(0);
	const itemsPerPage = 10;
	const showPage = 5;
	let totalPages = $state(0);
	let pagesToShow = $state([]);
	let totalItems = $state(0);
	let startPage;
	let endPage = $state(10);

	let items = $state([]);
	let loading = $state(true);

	// Fetch data from backend
	const fetchData = async () => {
		loading = true;
		try {
			const res = await fetch('http://localhost:5000/items', {credentials: 'include'});
			const data = await res.json();
			items = data;
			totalItems = items.length;
			renderPagination(items.length);
		} catch (err) {
			console.error('Failed to fetch items:', err);
		} finally {
			loading = false;
		}
	};

	const updateDataAndPagination = () => {
		let currentPageItems = items.slice(currentPosition, currentPosition + itemsPerPage);
		renderPagination(currentPageItems.length);
	};

	const loadNextPage = () => {
		if (currentPosition + itemsPerPage < items.length) {
			currentPosition += itemsPerPage;
			updateDataAndPagination();
		}
	};

	const loadPreviousPage = () => {
		if (currentPosition - itemsPerPage >= 0) {
			currentPosition -= itemsPerPage;
			updateDataAndPagination();
		}
	};

	const renderPagination = (totalItems) => {
		totalPages = Math.ceil(items.length / itemsPerPage);
		const currentPage = Math.ceil((currentPosition + 1) / itemsPerPage);

		startPage = currentPage - Math.floor(showPage / 2);
		startPage = Math.max(1, startPage);
		endPage = Math.min(startPage + showPage - 1, totalPages);

		pagesToShow = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
	};

	const goToPage = (pageNumber) => {
		currentPosition = (pageNumber - 1) * itemsPerPage;
		updateDataAndPagination();
	};

	let startRange = $derived(currentPosition + 1);
	let endRange = $derived(Math.min(currentPosition + itemsPerPage, totalItems));

	let currentPageItems = $derived(items.slice(currentPosition, currentPosition + itemsPerPage));
	let filteredItems = $derived(items.filter((item) => item.product_name.toLowerCase().includes(searchTerm.toLowerCase())));

	$effect(() => {
		// Fetch inventory data on mount
		fetchData();
	});
  
	/* ------------------  Add Item Side panel function ----------------------- */

	let hidden = $state(true);
	let selected = $state();
	let categories = [
		{ value: '', name: 'Select Type' },
		{ value: 'Fabric', name: 'Fabric' },
		{ value: 'Flooring', name: 'Flooring' },
		{ value: 'Furniture', name: 'Furniture' },
		{ value: 'Curtains', name: 'Curtains' },
		{ value: 'Tiles', name: 'Tiles' }
	];
	const handleCancel = () => {
		hidden = true;
	};

  let name = $state("");
  let manufacturer = $state("");
  let details = $state("");
  let number_items = $state(1);
  let image = $state("");
  let tags = $state("");

  let streamUrl = "http://localhost:5050";
  const media_url = "http://127.0.0.1:5000/media/";

	let imageUrl = $state("");
  imageUrl = "${streamUrl}";

  let description = $state("");
  let item_type = $state("");
  let location = $state("");
  let check_out_poc = $state("");
  let check_out_date = $state("");
  let is_checked_out = 0;

	let selectedFile = $state(null);

	async function handleFileUpload(Event) {
		const input = event.target;
		if (input.files && input.files.length > 0) {
			selectedFile = input.files[0];

			const formData = new FormData();
			formData.append("avatar", selectedFile);

			try {
				const response = await fetch("http://127.0.0.1:5000/image_upload", {
					method: "POST",
					body: formData,
				});

				if (response.ok) {
					const result = await response.json();
					image = result.image;
					imageUrl = `${media_url}/${image}.png`;
					showStaticImg = true;
					console.log("Upload successful:", result);
				} else {
					console.error("Upload failed:", await response.text());
				}
			} catch (error) {
				console.error("Error uploading file:", error);
			}
		}
	}

	/* ------------------  Additional functions ----------------------- */

	 async function downloadExcel() {
    const itemRes = await fetch('http://localhost:5000/items', {
      credentials: 'include'
    });

    const items = await itemRes.json();
    if (!items.length) return;

    // Convert JSON to worksheet
    const worksheet = XLSX.utils.json_to_sheet(items);

    // Create a new workbook and append the worksheet
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Inventory');

    // Generate timestamped filename
    const now = new Date();
    const timestamp = now.toISOString().replace(/[:.]/g, '-');
    const filename = `inventory-${timestamp}.xlsx`;

    // Write the workbook to a blob and trigger download
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
</script>

 <!-- ___________------------------ CONTENT --------------------____________ -->

<svelte:head>
  <title>Inventory</title>
  <meta name="description" content="Page to add new item" />
</svelte:head>

<Section name="advancedTable" sectionClass="w-full bg-gray-50 dark:bg-gray-900 p-3 sm:p-5">
	<TableSearch placeholder="Search" hoverable={true} bind:inputValue={searchTerm} {divClass} {innerDivClass} {searchClass}>
		{#snippet header()}
			<div class="flex w-full flex-shrink-0 flex-col items-stretch justify-end space-y-2 md:w-auto md:flex-row md:items-center md:space-y-0 md:space-x-3">
				<Button onclick={() => (hidden = false)}>
					<PlusOutline class="mr-2 h-3.5 w-3.5" />Add item
				</Button>
		    <Button >
					<QrCodeOutline class="mr-2 h-3.5 w-3.5" /> Scan QR
				</Button>
				<Button color="alternative">Actions<ChevronDownOutline class="ml-2 h-3 w-3 " /></Button>
				<Dropdown simple class="w-44 divide-y divide-gray-100">
					<DropdownItem onclick={downloadExcel} >Download Excel</DropdownItem>
					<DropdownItem>Delete all</DropdownItem>
				</Dropdown>
				<Button color="alternative">Filter<FilterSolid class="ml-2 h-3 w-3 " /></Button>
				<Dropdown class="w-48 space-y-2 p-3 text-sm">
					<h6 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">Choose manufacturer</h6>
					<List tag="dl">
						<Li>
							<Checkbox>Apple (56)</Checkbox>
						</Li>
						<Li>
							<Checkbox>Microsoft (16)</Checkbox>
						</Li>
						<Li>
							<Checkbox>Razor (49)</Checkbox>
						</Li>
						<Li>
							<Checkbox>Nikon (12)</Checkbox>
						</Li>
						<Li>
							<Checkbox>BenQ (74)</Checkbox>
						</Li>
					</List>
				</Dropdown>
			</div>
		{/snippet}
		<TableHead>
			<TableHeadCell class="px-4 py-3" scope="col">Product name</TableHeadCell>
			<TableHeadCell class="px-4 py-3" scope="col">Manufacturer</TableHeadCell>
			<TableHeadCell class="px-4 py-3" scope="col">Type</TableHeadCell>
			<TableHeadCell class="px-4 py-3" scope="col">Number of Items</TableHeadCell>
		</TableHead>
		<TableBody class="divide-y">
			{#if searchTerm !== ''}
				{#each filteredItems as item (item.id)}
					<TableBodyRow>
						<TableBodyCell class="px-4 py-3">{item.name}</TableBodyCell>
						<TableBodyCell class="px-4 py-3">{item.manufacturer}</TableBodyCell>
						<TableBodyCell class="px-4 py-3">{item.item_type}</TableBodyCell>
						<TableBodyCell class="px-4 py-3">{item.number_items}</TableBodyCell>
					</TableBodyRow>
				{/each}
			{:else}
				{#each currentPageItems as item (item.id)}
					<TableBodyRow>
						<TableBodyCell class="px-4 py-3">{item.name}</TableBodyCell>
						<TableBodyCell class="px-4 py-3">{item.manufacturer}</TableBodyCell>
						<TableBodyCell class="px-4 py-3">{item.item_type}</TableBodyCell>
						<TableBodyCell class="px-4 py-3">{item.number_items}</TableBodyCell>
					</TableBodyRow>
				{/each}
			{/if}
		</TableBody>
		{#snippet footer()}
			<div class="flex flex-col items-start justify-between space-y-3 p-4 md:flex-row md:items-center md:space-y-0" aria-label="Table navigation">
				<span class="text-sm font-normal text-gray-500 dark:text-gray-400">
					Showing
					<span class="font-semibold text-gray-900 dark:text-white">{startRange}-{endRange}</span>
					of
					<span class="font-semibold text-gray-900 dark:text-white">{totalItems}</span>
				</span>
				<ButtonGroup>
					<Button onclick={loadPreviousPage} disabled={currentPosition === 0}><ChevronLeftOutline size="xs" class="m-1.5" /></Button>
					{#each pagesToShow as pageNumber}
						<Button onclick={() => goToPage(pageNumber)}>{pageNumber}</Button>
					{/each}
					<Button onclick={loadNextPage} disabled={totalPages === endPage}><ChevronRightOutline size="xs" class="m-1.5" /></Button>
				</ButtonGroup>
			</div>
		{/snippet}
	</TableSearch>
</Section>



<Section name="advancedTable" sectionClass="w-full bg-gray-50 dark:bg-gray-900 p-3 sm:p-5">



</Section>

<!-- ---------------------   ADD ITEM SIDE PANEL --------------------------- -->

<Section name="crudcreatedrawer">
	<Drawer bind:hidden id="sidebar4" class="w-1/2">
		<div class="flex items-center justify-between">
			<h5 id="drawer-label" class="mb-6 inline-flex items-center text-base font-semibold text-gray-500 uppercase dark:text-gray-400">New Item</h5>
			<CloseButton onclick={handleCancel} class="mb-4 dark:text-white" />
		</div>
		<form action="#" class="mb-6">
			<div class="mb-6">
				<Label for="name" class="mb-2 block">Name</Label>
				<FloatingLabelInput clearable variant="outlined" id="clearable_outlined" name="clearable_outlined" type="text" required bind:value={name}>Name</FloatingLabelInput>
			</div>
			<div class="mb-6">
				<Label for="manufacturer" class="mb-2 block">Manufacturer</Label>
				<Input id="manufacturer" name="manufacturer" required placeholder="Item manufacturer" />
			</div>
			<div class="mb-6">
				<Label for="number_items" class="mb-2 block">Number of Items</Label>
				<Input id="number_items" name="prnumber_itemsice" required placeholder="1" />
			</div>
			<div class="mb-6">
				<Label
					>Item Type
					<Select class="mt-2" items={categories} bind:value={selected} />
				</Label>
			</div>
			<div class="mb-6">
				<Label for="brand" class="mb-2">Description</Label>
				<Textarea id="message" placeholder="Enter a detailed item description here" rows={4} name="message" />
			</div>

			<div class="items-center justify-center w-full">
					<label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-24 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
							<div class="flex flex-col items-center justify-center pt-5 pb-6">
									<svg class="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
											<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
									</svg>
									<p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
									<p class="text-xs text-gray-500 dark:text-gray-400">SVG, PNG, JPG </p>
							</div>
							<input id="dropzone-file" type="file" class="hidden" onchange={handleFileUpload} />
					</label>
			</div> 

			<div class="bottom-0 left-0 flex w-full justify-center space-x-4 pb-4 md:absolute md:px-4">
				<Button type="submit" class="w-full">Add item</Button>
				<Button class="w-full" color="light" onclick={handleCancel}>
					<svg aria-hidden="true" class="-ml-1 h-5 w-5 sm:mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"
						><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
					Cancel
				</Button>
			</div>
		</form>
	</Drawer>
</Section>


<!-- ---------------------   SCANNER CAMER SIDE PANEL --------------------------- -->
<!-- 
<Section name="scanner_sidepanel">
	<Drawer bind:hidden id="sidebar4" class="w-1/2">

	</Drawer>
</Section> -->