creqit.route_history_queue = [];
const routes_to_skip = ["Form", "social", "setup-wizard", "recorder"];

const save_routes = creqit.utils.debounce(() => {
	if (creqit.session.user === "Guest") return;
	const routes = creqit.route_history_queue;
	if (!routes.length) return;

	creqit.route_history_queue = [];

	creqit
		.xcall("creqit.desk.doctype.route_history.route_history.deferred_insert", {
			routes: routes,
		})
		.catch(() => {
			creqit.route_history_queue.concat(routes);
		});
}, 10000);

creqit.router.on("change", () => {
	const route = creqit.get_route();
	if (is_route_useful(route)) {
		creqit.route_history_queue.push({
			creation: creqit.datetime.now_datetime(),
			route: creqit.get_route_str(),
		});

		save_routes();
	}
});

function is_route_useful(route) {
	if (!route[1]) {
		return false;
	} else if ((route[0] === "List" && !route[2]) || routes_to_skip.includes(route[0])) {
		return false;
	} else {
		return true;
	}
}
